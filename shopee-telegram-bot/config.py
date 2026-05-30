import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")

# Shopee API Base URLs
SHOPEE_API_BASE = "https://shopee.co.id/api/v4"
SHOPEE_PRODUCT_API = f"{SHOPEE_API_BASE}/item/get"
SHOPEE_SHOP_API = f"{SHOPEE_API_BASE}/shop/get_shop_detail"
SHOPEE_SEARCH_API = f"{SHOPEE_API_BASE}/search/search_items"

# Tracking API
TRACKING_API_BASE = "https://shopee.co.id/api/v4/order/get_order_logistics"

# Headers untuk request ke Shopee
SHOPEE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://shopee.co.id/",
    "X-Requested-With": "XMLHttpRequest",
}

# Ongkir cities mapping (contoh beberapa kota besar)
CITY_MAPPING = {
    "jakarta": {"city_id": 152, "province_id": 6},
    "bandung": {"city_id": 23, "province_id": 9},
    "surabaya": {"city_id": 444, "province_id": 11},
    "semarang": {"city_id": 399, "province_id": 10},
    "yogyakarta": {"city_id": 501, "province_id": 5},
    "medan": {"city_id": 278, "province_id": 34},
    "makassar": {"city_id": 259, "province_id": 26},
    "palembang": {"city_id": 327, "province_id": 33},
    "denpasar": {"city_id": 114, "province_id": 1},
    "malang": {"city_id": 256, "province_id": 11},
    "solo": {"city_id": 445, "province_id": 10},
    "tangerang": {"city_id": 455, "province_id": 3},
    "bekasi": {"city_id": 54, "province_id": 9},
    "depok": {"city_id": 115, "province_id": 9},
    "bogor": {"city_id": 78, "province_id": 9},
    "batam": {"city_id": 48, "province_id": 21},
    "pekanbaru": {"city_id": 350, "province_id": 26},
    "balikpapan": {"city_id": 19, "province_id": 14},
    "pontianak": {"city_id": 365, "province_id": 12},
    "manado": {"city_id": 260, "province_id": 31},
}
