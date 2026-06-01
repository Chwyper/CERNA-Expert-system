import saka
from app import app, db
from models import Gejala, KataKunci

def seed_keywords():
    print("Mulai proses Seeding NLP Keywords menggunakan Saka-NLP...")
    
    with app.app_context():
        # Pastikan tabel sudah dibuat
        db.create_all()
        
        # Ambil semua gejala
        gejala_list = Gejala.query.all()
        if not gejala_list:
            print("Tabel Gejala kosong! Jalankan seed_database() terlebih dahulu.")
            return

        kata_tersimpan = 0
        
        stopwords_id = saka.get_stopwords('id')
        for gejala in gejala_list:
            # Bersihkan dan tokenisasi nama gejala
            tokens = saka.tokenize(gejala.nama.lower())
            
            # Filter stopword dan ambil akar kata
            for token in tokens:
                if token in stopwords_id:
                    continue
                
                # Cari akar kata menggunakan Heuristic Morphology Analyzer
                hasil_analisis = saka.analyze(token)
                akar_kata = hasil_analisis.get("root", token)
                
                # Jika panjang akar kata masuk akal (hindari karakter aneh)
                if len(akar_kata) > 2:
                    # Cek apakah keyword sudah ada untuk gejala ini
                    exists = KataKunci.query.filter_by(gejala_kode=gejala.kode, kata=akar_kata).first()
                    
                    if not exists:
                        # Tambahkan kata kunci
                        # Bobot default 0.8, mungkin bisa disesuaikan nanti
                        kw = KataKunci(gejala_kode=gejala.kode, kata=akar_kata, bobot=0.8)
                        db.session.add(kw)
                        kata_tersimpan += 1
                        print(f"[{gejala.kode}] Menambahkan kata kunci: {akar_kata}")
        
        db.session.commit()
        print(f"Seeding selesai! Berhasil menyimpan {kata_tersimpan} kata kunci NLP ke database.")

if __name__ == "__main__":
    seed_keywords()
