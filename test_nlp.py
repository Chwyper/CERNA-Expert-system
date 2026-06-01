from app import app
from nlp_engine import proses_pesan_chatbot
from engine import jalankan_diagnosa
import json

def test_chatbot():
    pesan_test = "aku sering sakit kepala banget dan akhir-akhir ini sulit tidur, juga sering keringat berlebih."
    print(f"\n--- Menguji NLP Pipeline ---")
    print(f"Pesan Pengguna: '{pesan_test}'")
    
    with app.app_context():
        # 1. Jalankan NLP Engine
        user_inputs = proses_pesan_chatbot(pesan_test)
        
        print("\n--- Menjalankan Diagnosa (Mesin CF) ---")
        # 2. Masukkan ke Engine CF
        if not user_inputs:
            print("Tidak ada gejala yang terdeteksi.")
            return
            
        hasil = jalankan_diagnosa(user_inputs)
        
        # 3. Urutkan berdasarkan persentase tertinggi
        hasil_sorted = sorted(hasil, key=lambda x: x['keyakinan'], reverse=True)
        
        # Ambil 3 teratas
        print("\n3 Prediksi Teratas:")
        for res in hasil_sorted[:3]:
            print(f"- {res['nama_penyakit']} ({res['keyakinan']}%) - Gejala cocok: {res['gejala_match']}/{res['total_gejala']}")

if __name__ == "__main__":
    test_chatbot()
