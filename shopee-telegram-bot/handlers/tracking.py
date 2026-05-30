"""Handler untuk cek resi pengiriman."""

from telegram import Update
from telegram.ext import ContextTypes
from services.tracking_api import TrackingAPI
from utils.formatter import format_tracking_info, format_error

tracking_api = TrackingAPI()


async def resi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk command /resi [nomor_resi] [kurir].
    
    Contoh:
    - /resi JN1234567890 jne
    - /resi SPXID1234567890
    - /resi 001234567890 sicepat
    """
    if not context.args:
        supported = tracking_api.get_supported_couriers()
        courier_list = "\n".join(supported)
        
        await update.message.reply_html(
            "❌ <b>Format salah!</b>\n\n"
            "Penggunaan:\n"
            "<code>/resi [nomor_resi]</code> - auto detect kurir\n"
            "<code>/resi [nomor_resi] [kurir]</code> - manual pilih kurir\n\n"
            "Contoh:\n"
            "<code>/resi JN1234567890</code>\n"
            "<code>/resi SPXID123456 spx</code>\n"
            "<code>/resi 001234567890 sicepat</code>\n\n"
            f"📋 <b>Kurir yang didukung:</b>\n{courier_list}"
        )
        return
    
    tracking_number = context.args[0].strip()
    courier = context.args[1].strip().lower() if len(context.args) > 1 else None
    
    # Kirim typing action
    await update.message.chat.send_action("typing")
    loading_msg = await update.message.reply_html("🔍 Mencari data resi...")
    
    # Track package
    tracking_data = await tracking_api.track_package(tracking_number, courier)
    
    if not tracking_data:
        await loading_msg.edit_text(
            format_error(
                "Tidak dapat menemukan data untuk resi tersebut.\n\n"
                "Pastikan:\n"
                "• Nomor resi benar\n"
                "• Kurir yang dipilih sesuai\n"
                "• Resi sudah terdaftar di sistem kurir"
            ),
            parse_mode="HTML"
        )
        return
    
    # Format dan kirim response
    message = format_tracking_info(tracking_data)
    
    # Tambah note jika demo mode
    if tracking_data.get("note"):
        message += f"\n\n⚠️ <i>{tracking_data['note']}</i>"
    
    await loading_msg.edit_text(message, parse_mode="HTML")
