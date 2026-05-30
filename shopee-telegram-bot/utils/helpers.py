"""Helper functions untuk bot."""

import re
from urllib.parse import urlparse, parse_qs


def extract_shopee_ids(url: str) -> tuple:
    """
    Extract shop_id dan item_id dari link Shopee.
    
    Supports formats:
    - https://shopee.co.id/product-name-i.shopid.itemid
    - https://shopee.co.id/product/shopid/itemid
    - https://shopee.co.id/shop/shopid/product/itemid
    
    Returns:
        tuple: (shop_id, item_id) atau (None, None) jika gagal
    """
    try:
        # Format: shopee.co.id/product-name-i.SHOPID.ITEMID
        pattern1 = r'i\.(\d+)\.(\d+)'
        match = re.search(pattern1, url)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Format: shopee.co.id/product/SHOPID/ITEMID
        pattern2 = r'/product/(\d+)/(\d+)'
        match = re.search(pattern2, url)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Format URL with query params
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'shop_id' in params and 'item_id' in params:
            return int(params['shop_id'][0]), int(params['item_id'][0])
        
        return None, None
    except (ValueError, IndexError):
        return None, None


def extract_shop_id(url: str) -> int:
    """Extract shop_id dari link toko Shopee."""
    try:
        # Format: shopee.co.id/shop/SHOPID
        pattern = r'/shop/(\d+)'
        match = re.search(pattern, url)
        if match:
            return int(match.group(1))
        
        # Format: shopee.co.id/SHOPNAME
        # Perlu API call untuk resolve username ke shop_id
        return None
    except (ValueError, IndexError):
        return None


def is_shopee_link(text: str) -> bool:
    """Cek apakah text mengandung link Shopee."""
    shopee_patterns = [
        r'shopee\.co\.id',
        r'shopee\.com',
        r'shp\.ee',
        r'shope\.ee',
    ]
    for pattern in shopee_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def is_short_link(url: str) -> bool:
    """Cek apakah url adalah short link Shopee yang perlu di-resolve."""
    short_markers = [
        "s.shopee.",      # s.shopee.co.id
        "shp.ee",
        "shope.ee",
        "/universal-link",
    ]
    low = url.lower()
    return any(m in low for m in short_markers)


def format_price(price: int) -> str:
    """Format harga ke format Rupiah."""
    return f"Rp {price:,.0f}".replace(",", ".")


def format_number(num: int) -> str:
    """Format angka dengan separator."""
    if num >= 1000000:
        return f"{num/1000000:.1f}jt"
    elif num >= 1000:
        return f"{num/1000:.1f}rb"
    return str(num)


def calculate_discount(original: int, discounted: int) -> int:
    """Hitung persentase diskon."""
    if original <= 0:
        return 0
    return round((1 - discounted / original) * 100)


def sanitize_text(text: str) -> str:
    """Sanitize text untuk Telegram markdown."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
