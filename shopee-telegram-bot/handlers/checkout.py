"""
Flow auto-checkout Shopee via ConversationHandler.

Alur:
  /beli -> cookie -> link produk -> (varian) -> jumlah -> ongkir
        -> voucher -> pembayaran -> konfirmasi -> checkout

⚠️  Melanggar ToS Shopee. Pakai dengan risiko sendiri. Cookie hanya disimpan
    di memori (context.user_data) selama sesi berlangsung.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from services.shopee_checkout import ShopeeCheckoutClient, ShopeeCheckoutError
from services.shopee_api import ShopeeAPI
from utils.helpers import extract_shopee_ids, format_price, is_short_link

shopee_api = ShopeeAPI()

# State
(COOKIE, LINK, VARIATION, QTY, SHIPPING, VOUCHER, PAYMENT, CONFIRM) = range(8)


# ---------------------------------------------------------------- entrypoint
async def beli_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai flow checkout, minta raw cookie."""
    context.user_data.clear()
    await update.message.reply_html(
        "🛒 <b>AUTO CHECKOUT SHOPEE</b>\n\n"
        "⚠️ <b>Peringatan:</b> Fitur ini melanggar ToS Shopee dan berisiko "
        "akun dibekukan. Gunakan dengan akun & risiko sendiri.\n\n"
        "<b>Langkah 1/7 — Login</b>\n"
        "Kirim <b>raw cookie</b> akun Shopee kamu.\n\n"
        "<i>Cara ambil cookie:</i> buka shopee.co.id di browser (sudah login) → "
        "F12 → tab Network → refresh → klik request apa saja → "
        "copy header <code>Cookie</code> → paste ke sini.\n\n"
        "🔒 Cookie hanya disimpan di memori selama sesi & pesanmu akan dihapus "
        "otomatis. Ketik /batal untuk membatalkan kapan saja."
    )
    return COOKIE


async def receive_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima cookie, verifikasi login."""
    raw_cookie = update.message.text.strip()

    # Hapus pesan cookie demi keamanan
    try:
        await update.message.delete()
    except Exception:
        pass

    if "csrftoken=" not in raw_cookie and "SPC_" not in raw_cookie:
        await update.effective_chat.send_message(
            "❌ Itu tidak terlihat seperti cookie Shopee yang valid.\n"
            "Pastikan kamu mem-paste seluruh isi header <code>Cookie</code>.\n"
            "Coba lagi, atau /batal.",
            parse_mode="HTML",
        )
        return COOKIE

    status = await update.effective_chat.send_message("⏳ Memverifikasi login...")
    client = ShopeeCheckoutClient(raw_cookie)

    try:
        info = await client.get_account_info()
    except ShopeeCheckoutError as e:
        await status.edit_text(f"❌ Login gagal: {e}\n\nKirim cookie lain atau /batal.")
        return COOKIE

    context.user_data["client"] = client
    username = info.get("username") or info.get("userid")
    await status.edit_text(
        f"✅ Login berhasil sebagai <b>{username}</b>\n\n"
        "<b>Langkah 2/7 — Produk</b>\n"
        "Kirim <b>link produk Shopee</b> yang mau dibeli.",
        parse_mode="HTML",
    )
    return LINK


async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima link produk, ambil detail & varian."""
    url = update.message.text.strip()

    # Resolve short link (s.shopee.co.id / shp.ee) ke full URL dulu
    if is_short_link(url):
        status0 = await update.message.reply_html("⏳ Memproses short link...")
        url = await shopee_api.resolve_short_link(url)
        try:
            await status0.delete()
        except Exception:
            pass

    shop_id, item_id = extract_shopee_ids(url)

    if not shop_id or not item_id:
        await update.message.reply_html(
            "❌ Link produk tidak valid / tidak bisa di-resolve.\n"
            "Kirim link produk Shopee yang benar (boleh short link), atau /batal."
        )
        return LINK

    status = await update.message.reply_html("⏳ Mengambil data produk...")
    client: ShopeeCheckoutClient = context.user_data["client"]

    # Ambil data produk pakai sesi login (cookie) - jauh lebih jarang diblok
    # dibanding request anonim.
    try:
        product = await client.get_product_detail(shop_id, item_id)
    except ShopeeCheckoutError as e:
        # Fallback: coba via koneksi anonim
        product = await shopee_api.get_product_detail(shop_id, item_id)
        if not product:
            await status.edit_text(
                f"❌ Gagal mengambil data produk.\n\n<b>Detail:</b> {e}\n\n"
                "Coba link lain atau /batal.",
                parse_mode="HTML",
            )
            return LINK

    context.user_data.update({
        "shop_id": shop_id,
        "item_id": item_id,
        "product_name": product.get("name", "Produk"),
        "stock": product.get("stock", 0),
        "models": product.get("models", []) or [],
    })

    models = context.user_data["models"]
    name = context.user_data["product_name"]

    # Bila ada beberapa varian, minta user memilih
    if len(models) > 1:
        keyboard = []
        for idx, m in enumerate(models):
            label = f"{m.get('name', 'Varian')} - {format_price(m.get('price', 0) // 100000)}"
            keyboard.append([InlineKeyboardButton(label[:60], callback_data=f"var:{idx}")])
        await status.edit_text(
            f"📦 <b>{name}</b>\n\n<b>Langkah 3/7 — Pilih Varian:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return VARIATION

    # Tanpa varian
    if models:
        context.user_data["model_id"] = models[0].get("modelid", 0)
    else:
        context.user_data["model_id"] = 0

    await status.edit_text(
        f"📦 <b>{name}</b>\nStok: {context.user_data['stock']}\n\n"
        "<b>Langkah 4/7 — Jumlah</b>\nKetik jumlah barang yang mau dibeli (angka).",
        parse_mode="HTML",
    )
    return QTY


async def select_variation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback pemilihan varian."""
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split(":")[1])
    model = context.user_data["models"][idx]
    context.user_data["model_id"] = model.get("modelid", 0)
    context.user_data["stock"] = model.get("stock", context.user_data.get("stock", 0))

    await query.edit_message_text(
        f"✅ Varian: <b>{model.get('name', '')}</b>\n"
        f"Stok: {context.user_data['stock']}\n\n"
        "<b>Langkah 4/7 — Jumlah</b>\nKetik jumlah barang yang mau dibeli (angka).",
        parse_mode="HTML",
    )
    return QTY


async def receive_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima jumlah, add to cart, lalu ambil opsi ongkir."""
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_html("❌ Jumlah harus angka lebih dari 0. Coba lagi atau /batal.")
        return QTY

    qty = int(text)
    stock = context.user_data.get("stock", 0)
    if stock and qty > stock:
        await update.message.reply_html(f"❌ Stok hanya {stock}. Masukkan jumlah lebih kecil.")
        return QTY

    context.user_data["quantity"] = qty
    client: ShopeeCheckoutClient = context.user_data["client"]
    shop_id = context.user_data["shop_id"]
    item_id = context.user_data["item_id"]
    model_id = context.user_data["model_id"]

    status = await update.message.reply_html("⏳ Menambahkan ke keranjang & mengambil opsi ongkir...")

    try:
        await client.add_to_cart(shop_id, item_id, model_id, qty)
        checkout_data = await client.checkout_get(shop_id, item_id, model_id, qty)
    except ShopeeCheckoutError as e:
        await status.edit_text(f"❌ {e}\n\nProses dihentikan. /batal untuk keluar.")
        return ConversationHandler.END

    context.user_data["checkout_data"] = checkout_data
    shipping = client.parse_shipping_options(checkout_data)
    context.user_data["shipping_options"] = shipping

    if not shipping:
        await status.edit_text(
            "⚠️ Tidak ada opsi ongkir terbaca dari respons Shopee (kemungkinan "
            "format anti-bot). Tidak bisa lanjut ke pemilihan ongkir.\n\n"
            "Ini batas yang dijelaskan di awal. /batal untuk keluar."
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(f"{s['name']} - {format_price(s['cost'] // 100000)}", callback_data=f"ship:{i}")]
        for i, s in enumerate(shipping)
    ]
    await status.edit_text(
        "<b>Langkah 5/7 — Pilih Ongkir:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SHIPPING


async def select_shipping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback pilih ongkir, lalu tampilkan voucher."""
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split(":")[1])
    context.user_data["shipping"] = context.user_data["shipping_options"][idx]

    client: ShopeeCheckoutClient = context.user_data["client"]
    vouchers = client.parse_vouchers(context.user_data["checkout_data"])
    context.user_data["vouchers"] = vouchers

    keyboard = [[InlineKeyboardButton("➡️ Tanpa voucher", callback_data="vou:-1")]]
    for i, v in enumerate(vouchers):
        label = v.get("voucher_code") or f"Voucher {i+1}"
        keyboard.insert(i, [InlineKeyboardButton(label[:60], callback_data=f"vou:{i}")])

    await query.edit_message_text(
        f"✅ Ongkir: <b>{context.user_data['shipping']['name']}</b>\n\n"
        "<b>Langkah 6/7 — Pilih Voucher:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return VOUCHER


async def select_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback pilih voucher, lalu tampilkan metode pembayaran."""
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split(":")[1])
    if idx >= 0 and idx < len(context.user_data.get("vouchers", [])):
        context.user_data["voucher"] = context.user_data["vouchers"][idx]
        voucher_label = context.user_data["voucher"].get("voucher_code", "Voucher")
    else:
        context.user_data["voucher"] = None
        voucher_label = "Tanpa voucher"

    client: ShopeeCheckoutClient = context.user_data["client"]
    channels = client.parse_payment_channels(context.user_data["checkout_data"])
    # Fallback channel umum bila tidak terbaca
    if not channels:
        channels = [
            {"channelid": 8, "name": "ShopeePay"},
            {"channelid": 3, "name": "Transfer Bank / VA"},
            {"channelid": 6, "name": "COD (Bayar di Tempat)"},
        ]
    context.user_data["payment_channels"] = channels

    keyboard = [
        [InlineKeyboardButton(c["name"], callback_data=f"pay:{i}")]
        for i, c in enumerate(channels)
    ]
    await query.edit_message_text(
        f"✅ Voucher: <b>{voucher_label}</b>\n\n"
        "<b>Langkah 7/7 — Pilih Pembayaran:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PAYMENT


async def select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback pilih pembayaran, tampilkan ringkasan & konfirmasi."""
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split(":")[1])
    context.user_data["payment"] = context.user_data["payment_channels"][idx]

    d = context.user_data
    summary = (
        "<b>📋 RINGKASAN PESANAN</b>\n\n"
        f"📦 Produk: {d['product_name']}\n"
        f"🔢 Jumlah: {d['quantity']}\n"
        f"🚚 Ongkir: {d['shipping']['name']} ({format_price(d['shipping']['cost'] // 100000)})\n"
        f"🎟️ Voucher: {d['voucher'].get('voucher_code') if d.get('voucher') else 'Tidak ada'}\n"
        f"💳 Pembayaran: {d['payment']['name']}\n\n"
        "Tekan <b>Checkout</b> untuk membuat pesanan."
    )
    keyboard = [[
        InlineKeyboardButton("✅ Checkout", callback_data="confirm:yes"),
        InlineKeyboardButton("❌ Batal", callback_data="confirm:no"),
    ]]
    await query.edit_message_text(summary, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback konfirmasi -> place_order."""
    query = update.callback_query
    await query.answer()

    if query.data.endswith(":no"):
        context.user_data.clear()
        await query.edit_message_text("❌ Checkout dibatalkan.")
        return ConversationHandler.END

    await query.edit_message_text("⏳ Memproses checkout...")
    client: ShopeeCheckoutClient = context.user_data["client"]

    # Bangun payload place_order dari checkout_data + pilihan user.
    # CATATAN: payload final Shopee sangat kompleks & butuh tanda tangan anti-bot.
    payload = dict(context.user_data.get("checkout_data", {}))
    payload["selected_payment_channel_data"] = {
        "channel_id": context.user_data["payment"].get("channelid"),
    }

    try:
        result = await client.place_order(payload)
    except ShopeeCheckoutError as e:
        await query.edit_message_text(
            f"❌ Checkout gagal: {e}\n\n"
            "Seperti diperingatkan di awal, endpoint place_order Shopee biasanya "
            "memblokir request tanpa tanda tangan anti-bot yang valid."
        )
        context.user_data.clear()
        return ConversationHandler.END

    await query.edit_message_text(
        f"✅ <b>Checkout berhasil!</b>\n\nRespons Shopee:\n<code>{str(result)[:500]}</code>",
        parse_mode="HTML",
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan flow."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_html("❌ Dibatalkan. Data sesi dihapus.")
    return ConversationHandler.END


def build_checkout_handler() -> ConversationHandler:
    """Bangun ConversationHandler untuk flow checkout."""
    return ConversationHandler(
        entry_points=[CommandHandler("beli", beli_start)],
        states={
            COOKIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cookie)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)],
            VARIATION: [CallbackQueryHandler(select_variation, pattern=r"^var:")],
            QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_quantity)],
            SHIPPING: [CallbackQueryHandler(select_shipping, pattern=r"^ship:")],
            VOUCHER: [CallbackQueryHandler(select_voucher, pattern=r"^vou:")],
            PAYMENT: [CallbackQueryHandler(select_payment, pattern=r"^pay:")],
            CONFIRM: [CallbackQueryHandler(confirm_order, pattern=r"^confirm:")],
        },
        fallbacks=[CommandHandler("batal", cancel), CommandHandler("cancel", cancel)],
        conversation_timeout=600,
    )
