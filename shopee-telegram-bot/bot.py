"""
🛒 Shopee Tools Telegram Bot
Bot Telegram untuk tools Shopee - cek produk, harga, resi, ongkir, dan toko.

Author: bagasadiik
"""

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN, PROXY_URL
from handlers import (
    start_command,
    help_command,
    cek_product_command,
    harga_command,
    auto_detect_link,
    resi_command,
    ongkir_command,
    toko_command,
)
from utils.formatter import format_help

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def callback_handler(update: Update, context):
    """Handler untuk inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await query.edit_message_text(
            format_help(),
            parse_mode="HTML"
        )
    
    elif query.data == "features":
        features_text = """🛒 <b>FITUR SHOPEE TOOLS BOT</b>

1️⃣ <b>Cek Produk</b>
Dapatkan informasi lengkap produk Shopee termasuk nama, harga, rating, stok, variasi, dan statistik penjualan.

2️⃣ <b>Cek Harga</b>
Cek harga real-time, diskon aktif, flash sale, dan range harga variasi produk.

3️⃣ <b>Tracking Resi</b>
Lacak status pengiriman paketmu dari berbagai kurir (JNE, J&T, SiCepat, Shopee Express, dll).

4️⃣ <b>Cek Ongkir</b>
Cek estimasi ongkos kirim antar kota dari berbagai jasa pengiriman.

5️⃣ <b>Info Toko</b>
Cek reputasi toko termasuk rating, jumlah pengikut, response rate, dan badge.

6️⃣ <b>Auto-detect Link</b>
Kirim link produk Shopee langsung dan bot akan otomatis menampilkan detailnya!

━━━━━━━━━━━━━━━━━
Kirim /help untuk panduan penggunaan."""

        keyboard = [[InlineKeyboardButton("📖 Cara Pakai", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(features_text, parse_mode="HTML", reply_markup=reply_markup)
    
    elif query.data == "guide_cek":
        text = """📦 <b>PANDUAN CEK PRODUK</b>

<b>Cara 1: Menggunakan command</b>
<code>/cek https://shopee.co.id/product-i.123.456</code>

<b>Cara 2: Kirim link langsung</b>
Salin link dari aplikasi Shopee, lalu paste langsung ke chat.

<b>Info yang ditampilkan:</b>
• Nama produk
• Harga & diskon
• Rating & ulasan
• Jumlah terjual
• Stok tersedia
• Variasi produk
• Lokasi toko

💡 <b>Tip:</b> Di aplikasi Shopee, tap tombol Share → Copy Link"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    elif query.data == "guide_resi":
        text = """🚚 <b>PANDUAN CEK RESI</b>

<b>Format:</b>
<code>/resi [nomor_resi]</code> - auto detect kurir
<code>/resi [nomor_resi] [kurir]</code> - pilih kurir

<b>Contoh:</b>
<code>/resi JN1234567890</code>
<code>/resi SPXID123456789 spx</code>

<b>Kurir yang didukung:</b>
• JNE (jne)
• J&T Express (jnt)
• SiCepat (sicepat)
• Shopee Express (spx)
• AnterAja (anteraja)
• ID Express (id-express)
• Ninja Express (ninja)
• POS Indonesia (pos)
• TIKI (tiki)

💡 <b>Tip:</b> Nomor resi bisa dicek di halaman pesanan Shopee"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    elif query.data == "guide_ongkir":
        text = """📊 <b>PANDUAN CEK ONGKIR</b>

<b>Format:</b>
<code>/ongkir [kota_asal] [kota_tujuan] [berat_gram]</code>

<b>Contoh:</b>
<code>/ongkir jakarta bandung 1000</code>
<code>/ongkir surabaya medan 500</code>
<code>/ongkir malang denpasar 2000</code>

<b>Kota yang tersedia:</b>
Jakarta, Bandung, Surabaya, Semarang, Yogyakarta, Medan, Makassar, Palembang, Denpasar, Malang, Solo, Tangerang, Bekasi, Depok, Bogor, Batam, Pekanbaru, Balikpapan, Pontianak, Manado

⚠️ Berat dalam satuan gram (1 kg = 1000 gram)"""
        await query.edit_message_text(text, parse_mode="HTML")
    
    elif query.data == "guide_toko":
        text = """🏪 <b>PANDUAN CEK TOKO</b>

<b>Format:</b>
<code>/toko [link_toko_shopee]</code>

<b>Contoh:</b>
<code>/toko https://shopee.co.id/shop/123456</code>
<code>/toko https://shopee.co.id/namatoko</code>

<b>Info yang ditampilkan:</b>
• Nama toko & badge
• Rating toko
• Jumlah pengikut
• Jumlah produk
• Response rate & time
• Lokasi toko

💡 <b>Tip:</b> Link toko bisa didapat dari halaman profil toko di Shopee"""
        await query.edit_message_text(text, parse_mode="HTML")


async def unknown_command(update: Update, context):
    """Handler untuk command yang tidak dikenal."""
    await update.message.reply_html(
        "❓ Command tidak dikenal.\n\n"
        "Kirim /help untuk melihat daftar command yang tersedia."
    )


async def post_init(application: Application):
    """Dijalankan sekali saat bot start: daftarkan menu command & deskripsi otomatis."""
    bot = application.bot
    commands = [
        BotCommand("start", "Mulai bot"),
        BotCommand("help", "Panduan penggunaan"),
        BotCommand("cek", "Cek detail produk Shopee"),
        BotCommand("harga", "Cek harga & diskon produk"),
        BotCommand("resi", "Lacak resi pengiriman"),
        BotCommand("ongkir", "Cek ongkos kirim antar kota"),
        BotCommand("toko", "Cek rating & info toko"),
    ]
    try:
        await bot.set_my_commands(commands)
        await bot.set_my_short_description(
            "Tools Shopee: cek produk, harga, resi, ongkir & toko."
        )
        await bot.set_my_description(
            "Bot tools Shopee. Cek detail produk, harga & diskon, lacak resi "
            "pengiriman, cek ongkir, dan rating toko. Cukup kirim link produk "
            "Shopee atau gunakan /help untuk daftar perintah."
        )
        me = await bot.get_me()
        logger.info("Bot @%s siap. Menu command & deskripsi berhasil didaftarkan.", me.username)
    except Exception as e:
        logger.warning("Gagal mendaftarkan command/deskripsi: %s", e)


def main():
    """Start the bot."""
    if not BOT_TOKEN:
        print("=" * 55)
        print("❌ Error: BOT_TOKEN belum diset!")
        print("=" * 55)
        print("Cara setting:")
        print("  1. Buka file .env di folder ini")
        print("  2. Isi baris: BOT_TOKEN=token_dari_BotFather")
        print("  3. Jalankan ulang script ini")
        print("\nBelum punya token? Chat @BotFather di Telegram, kirim /newbot")
        return
    
    # Build application dengan timeout panjang + dukungan proxy (opsional)
    builder = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .get_updates_read_timeout(30.0)
        .post_init(post_init)
    )

    if PROXY_URL:
        print(f"🔌 Menggunakan proxy: {PROXY_URL}")
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)

    app = builder.build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cek", cek_product_command))
    app.add_handler(CommandHandler("harga", harga_command))
    app.add_handler(CommandHandler("resi", resi_command))
    app.add_handler(CommandHandler("ongkir", ongkir_command))
    app.add_handler(CommandHandler("toko", toko_command))
    
    # Callback query handler (inline keyboard)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Auto-detect Shopee links
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        auto_detect_link
    ))
    
    # Unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Start polling
    print("🤖 Shopee Tools Bot is running...")
    print("Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
