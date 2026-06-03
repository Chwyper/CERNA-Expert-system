
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

    # Skenario 4: Paragraf Panjang Curhatan
    run_test(
        "SKENARIO 4: Paragraf Panjang Curhatan",
        "Halo dok, perkenalkan saya Budi. Saya akhir-akhir ini tuh merasa gampang capek setiap habis kerja. Terus yang paling mengganggu itu SAKIT KEPALA banget gatau kenapa padahal udah istirahat cukup. Trus ya gitu dehhh... nafasku kadang suka sesak padahal nggak ada riwayat asma atau alergi debu. Terus malamnya itu sumpah SUSAH banget buat tidur nyenyak. Kira-kira saya sakit apa ya dok?",
        ekspektasi_mengandung=["G09", "G10", "G01"], # Sakit kepala (G09), susah tidur (G10), sesak (G01)
        ekspektasi_TIDAK_mengandung=[]
    )
    
    # Skenario 5: Tanda Baca Berantakan dan Campur Kapitalisasi
    run_test(
        "SKENARIO 5: Tanda Baca Berantakan dan Campur Kapitalisasi",
        "dok...tolong,,,dada,,suka,,BERDEBAR-DEBAR gajelas?!, pdhl tdk pusing...tp sulit...tidur. knp ya dok???!!",
        ekspektasi_mengandung=["G02", "G10"], # dada berdebar (G02), sulit tidur (G10)
        ekspektasi_TIDAK_mengandung=["G09"] # pusing dinegasikan (tdk pusing)
    )
    
    # Skenario 6: Multiple Negation
    run_test(
        "SKENARIO 6: Multi-Negasi di Kalimat Kompleks",
        "hari ini saya tidak sesak nafas dan bukan pusing, cuma agak susah tidur aja",
        ekspektasi_mengandung=["G10"], # susah tidur
        ekspektasi_TIDAK_mengandung=["G01", "G09"] # sesak, pusing harus ke skip
    )

    # Skenario 7: Typo Parah (Salah Ketik)
    run_test(
        "SKENARIO 7: Typo Parah (Salah Ketik)",
        "dok kpla sya pusiiing bnget trs mual2 gtu, nafas jg sesek.",
        ekspektasi_mengandung=["G09", "G01"], # pusing (G09), sesak (G01)
        ekspektasi_TIDAK_mengandung=[] 
    )

    # Skenario 8: Kata Kiasan / Bahasa Gaul / Sinonim
    run_test(
        "SKENARIO 8: Kata Kiasan / Bahasa Gaul / Sinonim",
        "perut saya rasanya eneg, kepala mumet banget muter-muter, terus dada deg-degan.",
        ekspektasi_mengandung=["G09", "G02"], # mumet/muter -> pusing (G09), deg-degan -> dada berdebar (G02)
        ekspektasi_TIDAK_mengandung=[] 
    )

    # Skenario 9: Negasi Jarak Jauh (Long-Distance Negation)
    run_test(
        "SKENARIO 9: Negasi Jarak Jauh (Long-Distance Negation)",
        "saya tidak pernah merasa dada saya itu berdebar dok.",
        ekspektasi_mengandung=[], 
        ekspektasi_TIDAK_mengandung=["G02"] # berdebar (G02) dinegasi oleh "tidak" di awal
    )

    # Skenario 10: Kontradiksi Waktu (Dulu vs Sekarang)
    run_test(
        "SKENARIO 10: Kontradiksi Waktu (Dulu vs Sekarang)",
        "seminggu lalu emang pusing, tapi sekarang udah nggak pusing lagi, cuma tinggal susah tidur aja.",
        ekspektasi_mengandung=["G10"], # susah tidur (G10)
        ekspektasi_TIDAK_mengandung=["G09"] # pusing (G09) dinegasikan
    )

    # Skenario 11: Pemisahan Gejala Bertumpuk Tanpa Spasi
    run_test(
        "SKENARIO 11: Pemisahan Gejala Bertumpuk Tanpa Spasi",
        "sakitkepala banget dok, trus dada.berdebar.",
        ekspektasi_mengandung=["G09", "G02"], # sakit kepala (G09), dada berdebar (G02)
        ekspektasi_TIDAK_mengandung=[] 
    )

if __name__ == "__main__":
    main()

