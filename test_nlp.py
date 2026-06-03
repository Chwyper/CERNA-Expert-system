
from app import app
from nlp_engine import proses_pesan_chatbot
from engine import jalankan_diagnosa
import json

def run_test(nama_skenario, teks_input, ekspektasi_mengandung, ekspektasi_TIDAK_mengandung):
    print(f"\n{'='*50}")
    print(f"[TEST] MENGUJI: {nama_skenario}")
    print(f"Input: '{teks_input}'")
    print(f"{'='*50}")
    
    with app.app_context():
        user_inputs = proses_pesan_chatbot(teks_input)
        gejala_terdeteksi = list(user_inputs.keys())
        
        # Validasi positif (Harus ada)
        for g_kode in ekspektasi_mengandung:
            if g_kode in gejala_terdeteksi:
                print(f"[PASS] Gejala {g_kode} terdeteksi.")
            else:
                print(f"[FAIL] Gejala {g_kode} SEHARUSNYA terdeteksi namun hilang.")
                
        # Validasi negatif (Tidak Boleh ada)
        for g_kode in ekspektasi_TIDAK_mengandung:
            if g_kode in gejala_terdeteksi:
                print(f"[FAIL] Gejala {g_kode} TERDETEKSI (Padahal sudah dinegasi/tidak relevan).")
            else:
                print(f"[PASS] Gejala {g_kode} berhasil diabaikan/tidak ada.")

def main():
    # Skenario 1: Kasus Normal
    # G09 = sakit kepala / pusing, G10 = susah tidur / insomnia
    run_test(
        "SKENARIO 1: Kasus Ideal (Kalimat Jelas)",
        "aku sering sakit kepala banget dan akhir-akhir ini sulit tidur",
        ekspektasi_mengandung=["G09", "G10"],
        ekspektasi_TIDAK_mengandung=[]
    )
    
    # Skenario 2: Kasus Negasi (Anti-Salah Tangkap)
    # G09 (pusing) dinegasikan. G01 (sesak) tidak dinegasikan.
    run_test(
        "SKENARIO 2: Logika Negasi (Tidak / Bukan)",
        "saya tidak pusing dan gak susah tidur, tapi nafas agak sesak",
        ekspektasi_mengandung=["G01"], # Sesak
        ekspektasi_TIDAK_mengandung=["G09", "G10"] # Pusing dan Susah tidur harus di-skip
    )
    
    # Skenario 3: Kasus Slang & Kalimat Berantakan
    # SUSAH tidur (G10), dada berdebar (G02)
    run_test(
        "SKENARIO 3: Bahasa Gaul, Angka, & Kapitalisasi Acak",
        "aku tu akhir2 ini sering banget SUSAH tidur... trus dada suka berdebar gajelas gitu.",
        ekspektasi_mengandung=["G10", "G02"],
        ekspektasi_TIDAK_mengandung=[]
    )

if __name__ == "__main__":
    main()

