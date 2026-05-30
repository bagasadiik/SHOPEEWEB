# 🛒 Shopee Tools Telegram Bot

Bot Telegram untuk tools Shopee yang menyediakan berbagai fitur berguna untuk belanja di Shopee.

## ✨ Fitur

1. **📦 Cek Produk** - Dapatkan detail produk dari link Shopee (nama, harga, rating, stok, dll)
2. **💰 Cek Harga** - Cek harga real-time dan info diskon produk
3. **🚚 Cek Resi** - Tracking status pengiriman paket
4. **🔗 Convert Link** - Convert link Shopee ke short link / affiliate link
5. **📊 Cek Ongkir** - Cek ongkos kirim antar kota
6. **⭐ Cek Rating Toko** - Cek reputasi dan rating toko

## 🚀 Cara Install

### 1. Clone Repository
```bash
git clone https://github.com/bagasadiik/SHOPEEWEB.git
cd SHOPEEWEB/shopee-telegram-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi
Copy file `.env.example` ke `.env` dan isi dengan token bot Telegram kamu:
```bash
cp .env.example .env
```

Edit `.env`:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Dapatkan Bot Token
1. Buka Telegram, cari @BotFather
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot baru
4. Copy token yang diberikan

### 5. Jalankan Bot
```bash
python bot.py
```

## 📝 Cara Penggunaan

| Command | Deskripsi |
|---------|-----------|
| `/start` | Memulai bot |
| `/help` | Menampilkan bantuan |
| `/cek [link_shopee]` | Cek detail produk |
| `/harga [link_shopee]` | Cek harga produk |
| `/resi [nomor_resi]` | Tracking resi pengiriman |
| `/ongkir [asal] [tujuan] [berat]` | Cek ongkos kirim |
| `/toko [link_toko]` | Cek rating toko |

Atau cukup kirim **link produk Shopee** langsung, bot akan otomatis menampilkan detail produk.

## 🛠 Tech Stack

- Python 3.9+
- python-telegram-bot v20+
- aiohttp (async HTTP requests)
- BeautifulSoup4 (HTML parsing)

## 📁 Struktur Project

```
shopee-telegram-bot/
├── bot.py              # Main bot entry point
├── config.py           # Konfigurasi bot
├── requirements.txt    # Dependencies
├── .env.example        # Template environment variables
├── handlers/
│   ├── __init__.py
│   ├── start.py        # Handler /start & /help
│   ├── product.py      # Handler cek produk & harga
│   ├── tracking.py     # Handler cek resi
│   ├── shipping.py     # Handler cek ongkir
│   └── shop.py         # Handler cek toko
├── services/
│   ├── __init__.py
│   ├── shopee_api.py   # Shopee API service
│   ├── tracking_api.py # Tracking API service
│   └── shipping_api.py # Shipping/ongkir API service
└── utils/
    ├── __init__.py
    ├── formatter.py    # Format pesan
    └── helpers.py      # Helper functions
```

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi. Penggunaan bot ini sepenuhnya tanggung jawab pengguna.

## 📄 License

MIT License
