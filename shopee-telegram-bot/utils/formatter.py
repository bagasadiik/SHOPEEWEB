"""Message formatter untuk bot responses."""

from .helpers import format_price, format_number, calculate_discount


def format_product_detail(product_data: dict) -> str:
    """Format detail produk untuk ditampilkan di Telegram."""
    name = product_data.get("name", "N/A")
    price = product_data.get("price", 0) // 100000
    price_before = product_data.get("price_before_discount", 0) // 100000
    stock = product_data.get("stock", 0)
    sold = product_data.get("historical_sold", 0)
    rating = product_data.get("item_rating", {})
    rating_star = rating.get("rating_star", 0) if rating else 0
    rating_count = rating.get("rating_count", [0]*6) if rating else [0]*6
    total_rating = rating_count[0] if rating_count else 0
    liked = product_data.get("liked_count", 0)
    shop_location = product_data.get("shop_location", "N/A")
    
    # Hitung diskon
    discount_text = ""
    if price_before > price and price_before > 0:
        discount = calculate_discount(price_before, price)
        discount_text = f"\n🏷️ Diskon: {discount}% (dari {format_price(price_before)})"
    
    # Rating stars
    stars = "⭐" * round(rating_star) if rating_star > 0 else "Belum ada rating"
    
    message = f"""📦 <b>DETAIL PRODUK</b>

🏷️ <b>{name}</b>

💰 Harga: <b>{format_price(price)}</b>{discount_text}

📊 <b>Statistik:</b>
├ ⭐ Rating: {rating_star:.1f}/5.0 {stars}
├ 📝 Ulasan: {format_number(total_rating)}
├ 🛒 Terjual: {format_number(sold)}
├ ❤️ Disukai: {format_number(liked)}
└ 📦 Stok: {stock}

📍 Lokasi: {shop_location}
"""
    
    # Tambah info variasi jika ada
    models = product_data.get("models", [])
    if models and len(models) > 1:
        message += f"\n🎨 <b>Variasi ({len(models)}):</b>\n"
        for i, model in enumerate(models[:8]):  # Max 8 variasi
            model_name = model.get("name", "")
            model_price = model.get("price", 0) // 100000
            model_stock = model.get("stock", 0)
            message += f"  • {model_name} - {format_price(model_price)} (stok: {model_stock})\n"
        if len(models) > 8:
            message += f"  ... dan {len(models) - 8} variasi lainnya\n"
    
    return message


def format_price_info(product_data: dict) -> str:
    """Format info harga produk."""
    name = product_data.get("name", "N/A")
    price = product_data.get("price", 0) // 100000
    price_before = product_data.get("price_before_discount", 0) // 100000
    price_min = product_data.get("price_min", 0) // 100000
    price_max = product_data.get("price_max", 0) // 100000
    
    discount_text = ""
    if price_before > price and price_before > 0:
        discount = calculate_discount(price_before, price)
        discount_text = f"""
🏷️ <b>DISKON {discount}%!</b>
├ Harga Asli: <s>{format_price(price_before)}</s>
└ Hemat: {format_price(price_before - price)}"""
    
    range_text = ""
    if price_min != price_max and price_min > 0:
        range_text = f"\n📊 Range Harga: {format_price(price_min)} - {format_price(price_max)}"
    
    # Flash sale info
    flash_sale = product_data.get("flash_sale", None)
    flash_text = ""
    if flash_sale:
        flash_text = "\n\n⚡ <b>FLASH SALE AKTIF!</b>"
    
    # Upcoming sale
    upcoming = product_data.get("upcoming_flash_sale", None)
    upcoming_text = ""
    if upcoming:
        upcoming_text = "\n\n🔔 <b>Flash Sale Mendatang Tersedia!</b>"
    
    message = f"""💰 <b>INFO HARGA</b>

🏷️ <b>{name}</b>

💵 Harga: <b>{format_price(price)}</b>{discount_text}{range_text}{flash_text}{upcoming_text}

📈 <i>Harga dapat berubah sewaktu-waktu</i>
"""
    return message


def format_tracking_info(tracking_data: dict) -> str:
    """Format info tracking resi."""
    if not tracking_data:
        return "❌ Data tracking tidak ditemukan."
    
    courier = tracking_data.get("courier", "N/A")
    tracking_number = tracking_data.get("tracking_number", "N/A")
    status = tracking_data.get("status", "N/A")
    
    message = f"""🚚 <b>TRACKING PENGIRIMAN</b>

📋 No. Resi: <code>{tracking_number}</code>
🏢 Kurir: {courier}
📊 Status: <b>{status}</b>

📍 <b>Riwayat Pengiriman:</b>
"""
    
    activities = tracking_data.get("activities", [])
    for i, activity in enumerate(activities[:10]):
        time = activity.get("time", "")
        desc = activity.get("description", "")
        icon = "📍" if i == 0 else "  •"
        message += f"{icon} [{time}] {desc}\n"
    
    return message


def format_shipping_cost(shipping_data: list, origin: str, destination: str, weight: int) -> str:
    """Format info ongkos kirim."""
    if not shipping_data:
        return "❌ Data ongkir tidak ditemukan."
    
    message = f"""🚚 <b>CEK ONGKOS KIRIM</b>

📍 Asal: <b>{origin.title()}</b>
📍 Tujuan: <b>{destination.title()}</b>
⚖️ Berat: <b>{weight} gram</b>

📦 <b>Estimasi Ongkir:</b>
"""
    
    for courier in shipping_data:
        courier_name = courier.get("name", "N/A")
        services = courier.get("services", [])
        message += f"\n🏢 <b>{courier_name}</b>\n"
        for service in services[:3]:
            service_name = service.get("service", "")
            cost = service.get("cost", 0)
            etd = service.get("etd", "N/A")
            message += f"  • {service_name}: {format_price(cost)} ({etd} hari)\n"
    
    return message


def format_shop_info(shop_data: dict) -> str:
    """Format info toko."""
    name = shop_data.get("name", "N/A")
    rating = shop_data.get("rating_star", 0)
    followers = shop_data.get("follower_count", 0)
    products = shop_data.get("item_count", 0)
    response_rate = shop_data.get("response_rate", 0)
    response_time = shop_data.get("response_time", 0)
    joined = shop_data.get("ctime", 0)
    location = shop_data.get("shop_location", "N/A")
    is_official = shop_data.get("is_official_shop", False)
    is_preferred = shop_data.get("is_preferred_plus_seller", False)
    
    # Badge
    badge = ""
    if is_official:
        badge = "🏅 Official Shop"
    elif is_preferred:
        badge = "⭐ Star Seller"
    
    # Rating stars visual
    stars = "⭐" * round(rating) if rating > 0 else "Belum ada"
    
    message = f"""🏪 <b>INFO TOKO</b>

🏷️ <b>{name}</b> {badge}

📊 <b>Statistik:</b>
├ ⭐ Rating: {rating:.1f}/5.0 {stars}
├ 👥 Pengikut: {format_number(followers)}
├ 📦 Produk: {format_number(products)}
├ 💬 Response Rate: {response_rate}%
└ ⏱️ Response Time: dalam {response_time // 3600} jam

📍 Lokasi: {location}
"""
    return message


def format_error(error_msg: str) -> str:
    """Format pesan error."""
    return f"❌ <b>Error</b>\n\n{error_msg}"


def format_help() -> str:
    """Format pesan bantuan."""
    return """🛒 <b>SHOPEE TOOLS BOT</b>

Berikut fitur yang tersedia:

📦 <b>/cek [link]</b>
└ Cek detail produk Shopee

💰 <b>/harga [link]</b>
└ Cek harga & diskon produk

🚚 <b>/resi [nomor_resi] [kurir]</b>
└ Tracking status pengiriman
└ Kurir: jne, jnt, sicepat, anteraja, id-express

📦 <b>/ongkir [asal] [tujuan] [berat_gram]</b>
└ Cek ongkos kirim antar kota
└ Contoh: /ongkir jakarta bandung 1000

🏪 <b>/toko [link_toko]</b>
└ Cek info & rating toko

🔗 <b>Auto-detect</b>
└ Kirim link Shopee langsung, bot akan otomatis cek produk

━━━━━━━━━━━━━━━━━
💡 <b>Tips:</b> Salin link produk dari aplikasi Shopee lalu kirim ke bot ini!
"""
