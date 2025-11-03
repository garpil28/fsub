# utils/__init__.py
"""
Utils Package
-------------
Modul pendukung utama:
- db.py       → Koneksi MongoDB & fungsi simpan data
- license.py  → Validasi lisensi / akses pembeli
"""

from .db import Database
from .license import LicenseManager

__all__ = ["Database", "LicenseManager"]
