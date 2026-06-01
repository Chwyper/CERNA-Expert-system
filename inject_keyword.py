import json
import os
from app import app, db
from models import KataKunci, Gejala

def jalankan_injeksi():
    file_path = "keyword_for_inject2.json"
    
    # 1. Cek apakah file JSON ada
    if not os.path.exists(file_path):
        print(f"❌ File '{file_path}' tidak ditemukan!")
        print("Pastikan file ada.")
        return

    # 2. Baca file JSON
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data_baru = json.load(f)
        except json.JSONDecodeError:
            print("❌ File keyword_for_inject1.json tidak valid. Pastikan formatnya benar.")
            return
            
    # 3. Injeksi ke Database
    with app.app_context():
        kata_tersimpan = 0
        kata_dilewati = 0
        
        for item in data_baru:
            g_kode = item.get("gejala_kode")
            kata = item.get("kata", "").strip().lower()
            bobot = float(item.get("bobot", 0.8))
            
            # Validasi Gejala
            gejala_ada = Gejala.query.get(g_kode)
            if not gejala_ada or not kata:
                continue
                
            # Cek agar tidak ada kata duplikat untuk gejala yang sama
            exists = KataKunci.query.filter_by(gejala_kode=g_kode, kata=kata).first()
            if not exists:
                kw = KataKunci(gejala_kode=g_kode, kata=kata, bobot=bobot)
                db.session.add(kw)
                kata_tersimpan += 1
            else:
                kata_dilewati += 1
                
        db.session.commit()
        print("✅ PROSES SELESAI!")
        print(f"Total kata baru yang berhasil ditambahkan: {kata_tersimpan}")
        print(f"Total kata yang dilewati (sudah ada): {kata_dilewati}")

if __name__ == "__main__":
    print("Memulai injeksi kata kunci ke Database...")
    jalankan_injeksi()
