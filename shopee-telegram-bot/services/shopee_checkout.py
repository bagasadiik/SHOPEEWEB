"""
Shopee Checkout Client - login via raw cookie & melakukan flow checkout.

⚠️  PENTING / DISCLAIMER
    - Otomatisasi checkout MELANGGAR Terms of Service Shopee. Risiko akun
      dibekukan/banned ditanggung pengguna sendiri.
    - Shopee menerapkan proteksi anti-bot (tanda tangan request, device
      fingerprint, dll). Login via raw cookie SAJA sering tidak cukup untuk
      menembus endpoint checkout/place_order. Modul ini melakukan best-effort
      dan akan melaporkan error apa adanya bila diblokir.
    - Raw cookie = akses penuh ke akun. Jangan pernah dibagikan ke siapa pun.
"""

import re
import json
import time
import aiohttp

from config import get_ssl_param


class ShopeeCheckoutError(Exception):
    """Error khusus untuk proses checkout."""


class ShopeeCheckoutClient:
    """Client untuk login via raw cookie dan melakukan flow checkout Shopee."""

    BASE = "https://shopee.co.id/api/v4"

    def __init__(self, raw_cookie: str):
        self.raw_cookie = raw_cookie.strip()
        self.csrftoken = self._extract_cookie_value("csrftoken")

    # ------------------------------------------------------------------ utils
    def _extract_cookie_value(self, key: str) -> str:
        """Ambil value cookie tertentu dari raw cookie string."""
        m = re.search(rf"{re.escape(key)}=([^;]+)", self.raw_cookie)
        return m.group(1).strip() if m else ""

    def _headers(self, referer: str = "https://shopee.co.id/") -> dict:
        """Header standar untuk request ke API Shopee."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
            "Referer": referer,
            "Origin": "https://shopee.co.id",
            "X-Requested-With": "XMLHttpRequest",
            "X-API-SOURCE": "pc",
            "X-Shopee-Language": "id",
            "X-CSRFToken": self.csrftoken,
            "Cookie": self.raw_cookie,
        }

    async def _request(self, method: str, path: str, payload: dict = None,
                       params: dict = None, referer: str = "https://shopee.co.id/") -> dict:
        """Helper request async ke API Shopee."""
        url = f"{self.BASE}{path}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=payload,
                    params=params,
                    headers=self._headers(referer),
                    timeout=20,
                    ssl=get_ssl_param(),
                ) as resp:
                    text = await resp.text()
                    if resp.status != 200:
                        raise ShopeeCheckoutError(
                            f"HTTP {resp.status} dari {path}. "
                            "Kemungkinan diblok anti-bot atau cookie tidak valid."
                        )
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        raise ShopeeCheckoutError(
                            f"Respons bukan JSON dari {path} (kemungkinan halaman "
                            "verifikasi/anti-bot)."
                        )
        except aiohttp.ClientError as e:
            raise ShopeeCheckoutError(f"Gagal koneksi ke Shopee: {e}")

    # ------------------------------------------------------------------ auth
    async def get_account_info(self) -> dict:
        """
        Verifikasi login berdasarkan cookie.
        Returns dict info akun bila login valid, raise error bila tidak.
        """
        data = await self._request(
            "GET", "/account/basic/get_account_info"
        )
        # Bila tidak login, Shopee mengembalikan error / data kosong
        info = data.get("data") if isinstance(data, dict) else None
        if not info or not (info.get("username") or info.get("userid") or info.get("phone")):
            raise ShopeeCheckoutError(
                "Cookie tidak valid / sudah expired (tidak terdeteksi login)."
            )
        return info

    # ----------------------------------------------------------- product
    async def get_product_detail(self, shop_id: int, item_id: int) -> dict:
        """Ambil detail produk memakai sesi login (cookie)."""
        params = {"shopid": shop_id, "itemid": item_id}
        referer = f"https://shopee.co.id/product/{shop_id}/{item_id}"
        data = await self._request("GET", "/item/get", params=params, referer=referer)
        item = data.get("data") if isinstance(data, dict) else None
        if not item:
            err = data.get("error_msg") or data.get("error") if isinstance(data, dict) else None
            raise ShopeeCheckoutError(
                f"Produk kosong dari API Shopee (error={err})."
            )
        return item

    # --------------------------------------------------------------- cart
    async def add_to_cart(self, shop_id: int, item_id: int, model_id: int,
                          quantity: int) -> dict:
        """Tambahkan item ke keranjang (wajib sebelum checkout)."""
        payload = {
            "shopid": shop_id,
            "itemid": item_id,
            "modelid": model_id,
            "quantity": quantity,
            "checkout": True,
            "donot_add_quantity": False,
            "source": "{\"refer_urls\":[]}",
            "client_source": 1,
            "update_checkout_only": False,
        }
        referer = f"https://shopee.co.id/product/{shop_id}/{item_id}"
        data = await self._request("POST", "/cart/add_to_cart", payload=payload, referer=referer)
        if data.get("error"):
            raise ShopeeCheckoutError(
                f"Gagal add to cart: {data.get('error_msg') or data.get('error')}"
            )
        return data.get("data", {})

    # --------------------------------------------------------------- checkout
    async def checkout_get(self, shop_id: int, item_id: int, model_id: int,
                           quantity: int) -> dict:
        """
        Ambil informasi checkout (ongkir/logistik, voucher, channel pembayaran).
        Mengembalikan raw response /checkout/get untuk diproses lebih lanjut.
        """
        selected_item = {
            "shopid": shop_id,
            "itemid": item_id,
            "modelid": model_id,
            "quantity": quantity,
        }
        payload = {
            "shoporders": [
                {
                    "shopid": shop_id,
                    "items": [selected_item],
                }
            ],
            "selected_get_items": {str(item_id): [model_id]},
            "promotion_data": {"free_shipping_voucher_info": {}, "use_coins": False},
            "client_id": 0,
            "tax_info": {"tax_id": ""},
        }
        data = await self._request("POST", "/checkout/get", payload=payload)
        return data.get("data", data)

    def parse_shipping_options(self, checkout_data: dict) -> list:
        """Ambil daftar opsi logistik/ongkir dari respons checkout/get."""
        options = []
        try:
            shoporders = checkout_data.get("shoporders", [])
            for so in shoporders:
                logistics = so.get("shipping_list") or so.get("logistics", {}).get("logistics_channel_info", [])
                for ch in logistics:
                    options.append({
                        "channelid": ch.get("channelid") or ch.get("channel_id"),
                        "name": ch.get("name") or ch.get("channel_name", "Kurir"),
                        "cost": ch.get("price") or ch.get("cost", 0),
                    })
        except Exception:
            pass
        return options

    def parse_vouchers(self, checkout_data: dict) -> list:
        """Ambil daftar voucher yang bisa dipakai."""
        vouchers = []
        try:
            promo = checkout_data.get("promotion_data", {})
            for v in promo.get("platform_vouchers", []) or []:
                vouchers.append({
                    "promotionid": v.get("promotionid"),
                    "voucher_code": v.get("voucher_code", ""),
                    "discount": v.get("discount_value", 0),
                })
        except Exception:
            pass
        return vouchers

    def parse_payment_channels(self, checkout_data: dict) -> list:
        """Ambil daftar channel pembayaran yang tersedia."""
        channels = []
        try:
            for ch in checkout_data.get("payment_channel_list", []) or []:
                channels.append({
                    "channelid": ch.get("channel_id") or ch.get("channelid"),
                    "name": ch.get("channel_name") or ch.get("name", "Pembayaran"),
                })
        except Exception:
            pass
        return channels

    async def place_order(self, checkout_payload: dict) -> dict:
        """
        Eksekusi order final. checkout_payload harus berisi konfigurasi hasil
        checkout/get yang sudah diisi pilihan ongkir/voucher/pembayaran.

        CATATAN: endpoint ini paling ketat proteksi anti-bot-nya. Sangat mungkin
        diblokir tanpa tanda tangan request yang valid.
        """
        data = await self._request("POST", "/checkout/place_order", payload=checkout_payload)
        if data.get("error"):
            raise ShopeeCheckoutError(
                f"Gagal place order: {data.get('error_msg') or data.get('error')}"
            )
        return data.get("data", data)
