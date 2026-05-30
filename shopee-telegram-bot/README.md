# 🛒 Shopee Tools Telegram Bot

Bot Telegram untuk tools Shopee yang menyediakan berbagai fitur berguna untuk belanja di Shopee.

## ✨ Fitur

1. **📦 Cek Produk** - Dapatkan detail produk dari link Shopee (nama, harga, rating, stok, dll)
2. **💰 Cek Harga** - Cek harga real-time dan info diskon produk
3. **🚚 Cek Resi** - Tracking status pengiriman paket
4. **🔗 Convert Link** - Convert link Shopee ke short link / affiliate link
5. **📊 Cek Ongkir** - Cek ongkos kirim antar kota
6. **⭐ Cek Rating Toko** - Cek reputasi dan rating toko

## 🚀 Cara Tercepat (1 Perintah)

Bot otomatis bikin virtual environment, install dependencies, simpan token, lalu jalan.

**Linux / macOS:**
```bash
git clone -b feat/shopee-telegram-bot https://github.com/bagasadiik/SHOPEEWEB.git
cd SHOPEEWEB/shopee-telegram-bot
./run.sh TOKEN_DARI_BOTFATHER
```

**Windows:**
```bat
git clone -b feat/shopee-telegram-bot https://github.com/bagasadiik/SHOPEEWEB.git
cd SHOPEEWEB\shopee-telegram-bot
run.bat TOKEN_DARI_BOTFATHER
```

> Token cukup dimasukkan **sekali**. Selanjutnya cukup jalankan `./run.sh` (atau `run.bat`) tanpa argumen.

Saat pertama jalan, bot otomatis mendaftarkan menu command & deskripsi ke Telegram — jadi **tidak perlu setting manual di @BotFather**.

## 🐳 Alternatif: Docker

```bash
cp .env.example .env   # lalu isi BOT_TOKEN di file .env
docker compose up -d
```

## 🔧 Cara Manual (opsional)

```bash
pip install -r requirements.txt
cp .env.example .env       # isi BOT_TOKEN
python bot.py
```

### Dapatkan Bot Token
1. Buka Telegram, cari @BotFather
2. Kirim `/newbot`, ikuti instruksi
3. Copy token yang diberikan

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

## 🩺 Troubleshooting

### `telegram.error.TimedOut` / `httpx.ReadTimeout` saat start
Bot tidak bisa menjangkau `api.telegram.org`. Cek dulu:

```bash
curl -v --max-time 20 "https://api.telegram.org/bot<TOKEN>/getMe"
```

- Kalau muncul `{"ok":true,...}` → koneksi normal, mungkin cuma timeout sesaat, jalankan ulang.
- Kalau hang / timeout / connection refused → `api.telegram.org` **diblokir** oleh ISP/jaringanmu (umum terjadi di beberapa ISP Indonesia). Solusi: gunakan **proxy** atau **VPN**.

**Pakai proxy:** isi `PROXY_URL` di file `.env`, lalu jalankan ulang.
```
PROXY_URL=socks5://127.0.0.1:1080      # contoh SOCKS5
PROXY_URL=http://127.0.0.1:8080        # contoh HTTP proxy
```
Bot sudah otomatis pakai proxy bila `PROXY_URL` diisi. Alternatif paling simpel: nyalakan VPN lalu jalankan `./run.sh`.

## 🛠 Tech Stack
- Python 3.10+
- python-telegram-bot v21+
- aiohttp (async HTTP requests)

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
