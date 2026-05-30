"""Shopee API Service - untuk mengambil data produk dan toko dari Shopee."""

import aiohttp
import re
from config import SHOPEE_HEADERS, SHOPEE_API_BASE, get_ssl_param


class ShopeeAPI:
    """Service untuk berinteraksi dengan Shopee API."""
    
    def __init__(self):
        self.base_url = SHOPEE_API_BASE
        self.headers = SHOPEE_HEADERS
    
    async def get_product_detail(self, shop_id: int, item_id: int) -> dict:
        """
        Ambil detail produk dari Shopee API.
        
        Args:
            shop_id: ID toko
            item_id: ID produk
            
        Returns:
            dict: Data produk atau None jika gagal
        """
        url = f"{self.base_url}/item/get"
        params = {
            "shopid": shop_id,
            "itemid": item_id,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers, timeout=15, ssl=get_ssl_param()) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get("data"):
                            return data["data"]
                    return None
        except Exception as e:
            print(f"Error getting product detail: {e}")
            return None
    
    async def get_shop_detail(self, shop_id: int) -> dict:
        """
        Ambil detail toko dari Shopee API.
        
        Args:
            shop_id: ID toko
            
        Returns:
            dict: Data toko atau None jika gagal
        """
        url = f"{self.base_url}/shop/get_shop_detail"
        params = {
            "shopid": shop_id,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers, timeout=15, ssl=get_ssl_param()) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get("data"):
                            return data["data"]
                    return None
        except Exception as e:
            print(f"Error getting shop detail: {e}")
            return None
    
    async def get_shop_by_username(self, username: str) -> dict:
        """
        Ambil detail toko dari username/slug.
        
        Args:
            username: Username toko di Shopee
            
        Returns:
            dict: Data toko atau None jika gagal
        """
        url = f"{self.base_url}/shop/get_shop_detail"
        params = {
            "username": username,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers, timeout=15, ssl=get_ssl_param()) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get("data"):
                            return data["data"]
                    return None
        except Exception as e:
            print(f"Error getting shop by username: {e}")
            return None
    
    async def resolve_short_link(self, short_url: str) -> str:
        """
        Resolve short link Shopee (shp.ee) ke full URL.
        
        Args:
            short_url: Short URL dari Shopee
            
        Returns:
            str: Full URL atau original URL jika gagal
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    short_url, 
                    allow_redirects=False,
                    timeout=10,
                    ssl=get_ssl_param()
                ) as response:
                    if response.status in (301, 302):
                        location = response.headers.get("Location", short_url)
                        return location
                    return short_url
        except Exception as e:
            print(f"Error resolving short link: {e}")
            return short_url
    
    async def search_product(self, keyword: str, limit: int = 5) -> list:
        """
        Cari produk di Shopee.
        
        Args:
            keyword: Kata kunci pencarian
            limit: Jumlah hasil (default 5)
            
        Returns:
            list: List produk
        """
        url = f"{self.base_url}/search/search_items"
        params = {
            "by": "relevancy",
            "keyword": keyword,
            "limit": limit,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers, timeout=15, ssl=get_ssl_param()) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data.get("items"):
                            return data["items"]
                    return []
        except Exception as e:
            print(f"Error searching product: {e}")
            return []
