"""Handler untuk command /start dan /help."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.formatter import format_help


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start."""
    user = update.effective_user
    
    welcome_text = f"""👋 Halo <b>{user.first_name}</b>!

Selamat datang di <b>🛒 Shopee Tools Bot</b>

Bot ini membantu kamu untuk:
📦 Cek detail produk Shopee
💰 Cek harga & info diskon
🚚 Tracking resi pengiriman
📊 Cek ongkos kirim
🏪 Cek rating toko

Kirim /help untuk melihat semua perintah yang tersedia.

━━━━━━━━━━━━━━━━━
💡 <b>Quick Start:</b> Kirim link produk Shopee langsung ke chat ini!
"""
    
    # Inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("📖 Bantuan", callback_data="help"),
            InlineKeyboardButton("📦 Fitur", callback_data="features"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://github.com/bagasadiik"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help."""
    help_text = format_help()
    
    keyboard = [
        [
            InlineKeyboardButton("📦 Cek Produk", callback_data="guide_cek"),
            InlineKeyboardButton("🚚 Cek Resi", callback_data="guide_resi"),
        ],
        [
            InlineKeyboardButton("📊 Cek Ongkir", callback_data="guide_ongkir"),
            InlineKeyboardButton("🏪 Cek Toko", callback_data="guide_toko"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(help_text, reply_markup=reply_markup)
