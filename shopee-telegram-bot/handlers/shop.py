"""Handler untuk cek info toko Shopee."""

import re
from telegram import Update
from telegram.ext import ContextTypes
from services.shopee_api import ShopeeAPI
from utils.helpers import extract_shop_id
from utils.formatter import format_shop_info, format_error

shopee_api = ShopeeAPI()


async def toko_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk command /toko [link_toko].
    
    Contoh:
    - /toko https://shopee.co.id/shop/123456
    - /toko https://shopee.co.id/namatoko
    """
    if not context.args:
        await update.message.reply_html(
            "❌ <b>Format salah!</b>\n\n"
            "Penggunaan:\n"
            "<code>/toko [link_toko_shopee]</code>\n\n"
            "Contoh:\n"
            "<code>/toko https://shopee.co.id/shop/123456</code>\n"
            "<code>/toko https://shopee.co.id/namatoko</code>"
        )
        return
    
    url = context.args[0].strip()
    
    # Kirim typing action
    await update.message.chat.send_action("typing")
    loading_msg = await update.message.reply_html("🔍 Mencari info toko...")
    
    shop_data = None
    
    # Coba extract shop_id dari URL
    shop_id = extract_shop_id(url)
    
    if shop_id:
        shop_data = await shopee_api.get_shop_detail(shop_id)
    else:
        # Coba extract username dari URL
        # Format: shopee.co.id/USERNAME
        username_pattern = r'shopee\.co\.id/([^/?#\s]+)'
        match = re.search(username_pattern, url)
        
        if match:
            username = match.group(1)
            # Filter out non-shop URLs
            excluded_paths = ['product', 'shop', 'daily_discover', 'search', 'cart', 'buyer']
            if username not in excluded_paths:
                shop_data = await shopee_api.get_shop_by_username(username)
    
    if not shop_data:
        await loading_msg.edit_text(
            format_error(
                "Tidak dapat menemukan toko tersebut.\n\n"
                "Pastikan:\n"
                "• Link toko valid\n"
                "• Toko masih aktif di Shopee\n\n"
                "Format yang didukung:\n"
                "• https://shopee.co.id/shop/SHOPID\n"
                "• https://shopee.co.id/NAMATOKO"
            ),
            parse_mode="HTML"
        )
        return
    
    # Format dan kirim response
    message = format_shop_info(shop_data)
    message += f"\n🔗 <a href='{url}'>Buka Toko di Shopee</a>"
    
    await loading_msg.edit_text(message, parse_mode="HTML", disable_web_page_preview=True)
