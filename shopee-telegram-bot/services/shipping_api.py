"""Shipping API Service - untuk cek ongkos kirim."""

import aiohttp
from config import CITY_MAPPING


class ShippingAPI:
    """Service untuk cek ongkos kirim."""
    
    def __init__(self):
        # Menggunakan RajaOngkir API (free tier)
        # Daftar di https://rajaongkir.com untuk mendapat API key
        self.api_key = "free"  # Ganti dengan API key RajaOngkir
        self.base_url = "https://api.rajaongkir.com/starter"
    
    async def check_cost(self, origin: str, destination: str, weight: int) -> list:
        """
        Cek ongkos kirim.
        
        Args:
            origin: Kota asal
            destination: Kota tujuan
            weight: Berat dalam gram
            
        Returns:
            list: List ongkir per kurir
        """
        origin_lower = origin.lower().strip()
        dest_lower = destination.lower().strip()
        
        # Cek kota di mapping
        origin_city = CITY_MAPPING.get(origin_lower)
        dest_city = CITY_MAPPING.get(dest_lower)
        
        if not origin_city:
            return None, f"Kota asal '{origin}' tidak ditemukan. Gunakan nama kota besar (jakarta, bandung, surabaya, dll)"
        
        if not dest_city:
            return None, f"Kota tujuan '{destination}' tidak ditemukan. Gunakan nama kota besar (jakarta, bandung, surabaya, dll)"
        
        # Coba API RajaOngkir
        try:
            result = await self._call_rajaongkir(
                origin_city["city_id"],
                dest_city["city_id"],
                weight
            )
            if result:
                return result, None
        except Exception as e:
            print(f"Error calling RajaOngkir: {e}")
        
        # Fallback: estimasi ongkir
        return self._generate_estimated_cost(origin, destination, weight), None
    
    async def _call_rajaongkir(self, origin_id: int, dest_id: int, weight: int) -> list:
        """Call RajaOngkir API."""
        url = f"{self.base_url}/cost"
        headers = {
            "key": self.api_key,
            "content-type": "application/x-www-form-urlencoded"
        }
        data = {
            "origin": origin_id,
            "destination": dest_id,
            "weight": weight,
            "courier": "jne:jnt:sicepat"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data, timeout=15) as response:
                    if response.status == 200:
                        result = await response.json()
                        rajaongkir = result.get("rajaongkir", {})
                        results = rajaongkir.get("results", [])
                        
                        if results:
                            return self._parse_rajaongkir_response(results)
            return None
        except Exception:
            return None
    
    def _parse_rajaongkir_response(self, results: list) -> list:
        """Parse response dari RajaOngkir."""
        couriers = []
        for courier in results:
            services = []
            for cost in courier.get("costs", []):
                cost_detail = cost.get("cost", [{}])[0]
                services.append({
                    "service": cost.get("service", ""),
                    "description": cost.get("description", ""),
                    "cost": cost_detail.get("value", 0),
                    "etd": cost_detail.get("etd", "N/A"),
                })
            couriers.append({
                "name": courier.get("name", ""),
                "code": courier.get("code", ""),
                "services": services,
            })
        return couriers
    
    def _generate_estimated_cost(self, origin: str, destination: str, weight: int) -> list:
        """Generate estimasi ongkir berdasarkan zona."""
        # Tentukan zona (sama kota, sama pulau, beda pulau)
        base_cost = self._calculate_base_cost(origin, destination, weight)
        
        return [
            {
                "name": "JNE",
                "code": "jne",
                "services": [
                    {"service": "REG", "cost": base_cost, "etd": "2-3"},
                    {"service": "YES", "cost": int(base_cost * 1.8), "etd": "1"},
                    {"service": "OKE", "cost": int(base_cost * 0.8), "etd": "3-5"},
                ]
            },
            {
                "name": "J&T Express",
                "code": "jnt",
                "services": [
                    {"service": "EZ", "cost": int(base_cost * 0.9), "etd": "2-4"},
                    {"service": "JSD", "cost": int(base_cost * 1.5), "etd": "1"},
                ]
            },
            {
                "name": "SiCepat",
                "code": "sicepat",
                "services": [
                    {"service": "REG", "cost": int(base_cost * 0.85), "etd": "2-3"},
                    {"service": "BEST", "cost": int(base_cost * 1.2), "etd": "1-2"},
                ]
            },
            {
                "name": "Shopee Express",
                "code": "spx",
                "services": [
                    {"service": "Standard", "cost": int(base_cost * 0.75), "etd": "3-5"},
                    {"service": "Hemat", "cost": int(base_cost * 0.6), "etd": "4-7"},
                ]
            },
        ]
    
    def _calculate_base_cost(self, origin: str, destination: str, weight: int) -> int:
        """Hitung base cost berdasarkan zona."""
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Pulau Jawa
        jawa_cities = ["jakarta", "bandung", "surabaya", "semarang", "yogyakarta", 
                       "malang", "solo", "tangerang", "bekasi", "depok", "bogor"]
        
        # Sama kota
        if origin_lower == dest_lower:
            per_kg = 8000
        # Sama pulau (Jawa)
        elif origin_lower in jawa_cities and dest_lower in jawa_cities:
            per_kg = 12000
        # Beda pulau tapi dekat
        elif (origin_lower in jawa_cities and dest_lower in ["denpasar", "palembang", "batam"]) or \
             (dest_lower in jawa_cities and origin_lower in ["denpasar", "palembang", "batam"]):
            per_kg = 18000
        # Beda pulau jauh
        else:
            per_kg = 25000
        
        # Hitung berdasarkan berat (minimum 1kg)
        weight_kg = max(1, weight / 1000)
        return int(per_kg * weight_kg)
    
    def get_supported_cities(self) -> list:
        """Dapatkan list kota yang didukung."""
        return sorted(CITY_MAPPING.keys())
