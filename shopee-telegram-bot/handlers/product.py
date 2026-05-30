"""Handler untuk cek produk dan harga Shopee."""

from telegram import Update
from telegram.ext import ContextTypes
from services.shopee_api import ShopeeAPI
from utils.helpers import extract_shopee_ids, is_shopee_link, is_short_link
from utils.formatter import format_product_detail, format_price_info, format_error

shopee_api = ShopeeAPI()


async def cek_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /cek [link_shopee]."""
    if not context.args:
        await update.message.reply_html(
            "❌ <b>Format salah!</b>\n\n"
            "Penggunaan: <code>/cek [link_produk_shopee]</code>\n\n"
            "Contoh:\n"
            "<code>/cek https://shopee.co.id/product-i.123.456</code>"
        )
        return
    
    url = context.args[0]
    await _process_product_link(update, url, mode="detail")


async def harga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /harga [link_shopee]."""
    if not context.args:
        await update.message.reply_html(
            "❌ <b>Format salah!</b>\n\n"
            "Penggunaan: <code>/harga [link_produk_shopee]</code>\n\n"
            "Contoh:\n"
            "<code>/harga https://shopee.co.id/product-i.123.456</code>"
        )
        return
    
    url = context.args[0]
    await _process_product_link(update, url, mode="price")


async def auto_detect_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-detect link Shopee yang dikirim user."""
    text = update.message.text
    
    if not is_shopee_link(text):
        return
    
    # Extract URL dari text
    import re
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        # Mungkin short link tanpa http
        if "shp.ee" in text or "shopee" in text:
            urls = [text.strip()]
    
    if urls:
        await _process_product_link(update, urls[0], mode="detail")


async def _process_product_link(update: Update, url: str, mode: str = "detail"):
    """Process link produk Shopee."""
    # Kirim typing action
    await update.message.chat.send_action("typing")
    
    # Resolve short link jika perlu
    if is_short_link(url):
        loading_msg = await update.message.reply_html("⏳ Memproses short link...")
        url = await shopee_api.resolve_short_link(url)
        await loading_msg.delete()
    
    # Extract shop_id dan item_id
    shop_id, item_id = extract_shopee_ids(url)
    
    if not shop_id or not item_id:
        await update.message.reply_html(
            format_error(
                "Tidak dapat mengekstrak ID produk dari link tersebut.\n\n"
                "Pastikan link yang dikirim adalah link produk Shopee yang valid.\n"
                "Contoh: https://shopee.co.id/product-name-i.SHOPID.ITEMID"
            )
        )
        return
    
    # Ambil data produk
    loading_msg = await update.message.reply_html("⏳ Mengambil data produk...")
    product_data = await shopee_api.get_product_detail(shop_id, item_id)
    
    if not product_data:
        await loading_msg.edit_text(
            format_error(
                "Gagal mengambil data produk. Kemungkinan:\n"
                "• Produk sudah dihapus\n"
                "• Link tidak valid\n"
                "• Server Shopee sedang sibuk\n\n"
                "Silakan coba lagi nanti."
            ),
            parse_mode="HTML"
        )
        return
    
    # Format dan kirim response
    if mode == "detail":
        message = format_product_detail(product_data)
    elif mode == "price":
        message = format_price_info(product_data)
    else:
        message = format_product_detail(product_data)
    
    # Tambahkan link produk
    message += f"\n🔗 <a href='{url}'>Buka di Shopee</a>"
    
    await loading_msg.edit_text(message, parse_mode="HTML", disable_web_page_preview=True)
