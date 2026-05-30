"""Handler untuk cek ongkos kirim."""

from telegram import Update
from telegram.ext import ContextTypes
from services.shipping_api import ShippingAPI
from utils.formatter import format_shipping_cost, format_error

shipping_api = ShippingAPI()


async def ongkir_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk command /ongkir [asal] [tujuan] [berat_gram].
    
    Contoh:
    - /ongkir jakarta bandung 1000
    - /ongkir surabaya medan 500
    """
    if len(context.args) < 3:
        cities = shipping_api.get_supported_cities()
        city_list = ", ".join(cities[:15])
        
        await update.message.reply_html(
            "❌ <b>Format salah!</b>\n\n"
            "Penggunaan:\n"
            "<code>/ongkir [kota_asal] [kota_tujuan] [berat_gram]</code>\n\n"
            "Contoh:\n"
            "<code>/ongkir jakarta bandung 1000</code>\n"
            "<code>/ongkir surabaya medan 500</code>\n"
            "<code>/ongkir malang denpasar 2000</code>\n\n"
            f"🏙️ <b>Kota yang tersedia:</b>\n{city_list}, ..."
        )
        return
    
    origin = context.args[0].strip()
    destination = context.args[1].strip()
    
    try:
        weight = int(context.args[2])
        if weight <= 0:
            raise ValueError("Weight must be positive")
        if weight > 30000:
            await update.message.reply_html(
                format_error("Berat maksimal 30.000 gram (30 kg)")
            )
            return
    except ValueError:
        await update.message.reply_html(
            format_error("Berat harus berupa angka dalam satuan gram.\nContoh: /ongkir jakarta bandung 1000")
        )
        return
    
    # Kirim typing action
    await update.message.chat.send_action("typing")
    loading_msg = await update.message.reply_html("📊 Menghitung ongkos kirim...")
    
    # Cek ongkir
    shipping_data, error = await shipping_api.check_cost(origin, destination, weight)
    
    if error:
        await loading_msg.edit_text(format_error(error), parse_mode="HTML")
        return
    
    if not shipping_data:
        await loading_msg.edit_text(
            format_error("Gagal menghitung ongkos kirim. Silakan coba lagi."),
            parse_mode="HTML"
        )
        return
    
    # Format dan kirim response
    message = format_shipping_cost(shipping_data, origin, destination, weight)
    message += "\n⚠️ <i>Harga bersifat estimasi dan dapat berbeda dengan harga actual di Shopee</i>"
    
    await loading_msg.edit_text(message, parse_mode="HTML")
