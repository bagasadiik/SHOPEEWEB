"""Tracking API Service - untuk cek resi pengiriman."""

import aiohttp


# Mapping kurir yang didukung
COURIER_MAPPING = {
    "jne": {
        "name": "JNE",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "jne"
    },
    "jnt": {
        "name": "J&T Express",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "jnt"
    },
    "sicepat": {
        "name": "SiCepat",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "sicepat"
    },
    "anteraja": {
        "name": "AnterAja",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "anteraja"
    },
    "id-express": {
        "name": "ID Express",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "ide"
    },
    "pos": {
        "name": "POS Indonesia",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "pos"
    },
    "tiki": {
        "name": "TIKI",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "tiki"
    },
    "ninja": {
        "name": "Ninja Express",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "ninja"
    },
    "spx": {
        "name": "Shopee Express",
        "api_url": "https://api.binderbyte.com/v1/track",
        "code": "spx"
    },
}


class TrackingAPI:
    """Service untuk tracking resi pengiriman."""
    
    def __init__(self):
        # Menggunakan free API dari binderbyte (perlu API key)
        # User bisa daftar gratis di https://binderbyte.com
        self.api_key = "free"  # Ganti dengan API key sendiri
    
    async def track_package(self, tracking_number: str, courier: str = None) -> dict:
        """
        Track paket berdasarkan nomor resi.
        
        Args:
            tracking_number: Nomor resi
            courier: Kode kurir (opsional, akan auto-detect jika tidak disertakan)
            
        Returns:
            dict: Data tracking
        """
        # Auto-detect courier dari format resi
        if not courier:
            courier = self._detect_courier(tracking_number)
        
        courier_lower = courier.lower() if courier else ""
        courier_info = COURIER_MAPPING.get(courier_lower)
        
        if not courier_info:
            return self._generate_demo_tracking(tracking_number, courier or "Unknown")
        
        # Coba gunakan API tracking
        try:
            url = courier_info["api_url"]
            params = {
                "api_key": self.api_key,
                "courier": courier_info["code"],
                "awb": tracking_number,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == 200:
                            return self._parse_tracking_response(data, courier_info["name"])
            
            # Jika API gagal, return demo data
            return self._generate_demo_tracking(tracking_number, courier_info["name"])
            
        except Exception as e:
            print(f"Error tracking package: {e}")
            return self._generate_demo_tracking(tracking_number, courier_info["name"])
    
    def _detect_courier(self, tracking_number: str) -> str:
        """Auto-detect kurir dari format nomor resi."""
        tn = tracking_number.upper()
        
        # JNE pattern
        if tn.startswith("JN") or tn.startswith("CGK"):
            return "jne"
        # J&T pattern  
        elif tn.startswith("J") and len(tn) >= 12:
            return "jnt"
        # SiCepat pattern
        elif tn.startswith("00") and len(tn) >= 12:
            return "sicepat"
        # Shopee Express
        elif tn.startswith("SPX") or tn.startswith("SPXID"):
            return "spx"
        # AnterAja
        elif tn.startswith("1") and len(tn) == 14:
            return "anteraja"
        # ID Express
        elif tn.startswith("IDE"):
            return "id-express"
        # Ninja Express
        elif tn.startswith("NV") or tn.startswith("NLID"):
            return "ninja"
        # TIKI
        elif tn.startswith("03") and len(tn) == 10:
            return "tiki"
        
        return None
    
    def _parse_tracking_response(self, data: dict, courier_name: str) -> dict:
        """Parse response dari tracking API."""
        result = data.get("data", {})
        summary = result.get("summary", {})
        history = result.get("history", [])
        
        activities = []
        for item in history:
            activities.append({
                "time": item.get("date", ""),
                "description": item.get("desc", ""),
            })
        
        return {
            "tracking_number": summary.get("awb", ""),
            "courier": courier_name,
            "status": summary.get("status", "Unknown"),
            "service": summary.get("service", ""),
            "origin": summary.get("origin", ""),
            "destination": summary.get("destination", ""),
            "activities": activities,
        }
    
    def _generate_demo_tracking(self, tracking_number: str, courier_name: str) -> dict:
        """Generate demo tracking data untuk demonstrasi."""
        return {
            "tracking_number": tracking_number,
            "courier": courier_name,
            "status": "⚠️ Demo Mode - Silakan isi API key untuk tracking real",
            "activities": [
                {
                    "time": "2024-01-15 10:30",
                    "description": "📍 Paket telah diterima oleh penerima"
                },
                {
                    "time": "2024-01-15 08:00",
                    "description": "🚚 Paket sedang diantar ke alamat tujuan"
                },
                {
                    "time": "2024-01-14 20:00",
                    "description": "📦 Paket tiba di gudang sorting tujuan"
                },
                {
                    "time": "2024-01-14 10:00",
                    "description": "🚛 Paket dalam perjalanan ke kota tujuan"
                },
                {
                    "time": "2024-01-13 15:00",
                    "description": "📦 Paket dipickup dari seller"
                },
            ],
            "note": "Ini adalah demo. Daftar API key gratis di binderbyte.com untuk tracking real."
        }
    
    def get_supported_couriers(self) -> list:
        """Dapatkan list kurir yang didukung."""
        return [
            f"• {info['name']} ({code})" 
            for code, info in COURIER_MAPPING.items()
        ]
