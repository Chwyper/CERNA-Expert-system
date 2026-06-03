
from app import app
from nlp_engine import proses_pesan_chatbot
from engine import jalankan_diagnosa
import json

def run_test(nama_skenario, teks_input, ekspektasi_mengandung, ekspektasi_TIDAK_mengandung):
    print(f"\n{'='*50}")
    print(f"[TEST] MENGUJI: {nama_skenario}")
    print(f"Input: '{teks_input}'")
    print(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    with app.app_context():
        user_inputs = proses_pesan_chatbot(teks_input)
        gejala_terdeteksi = list(user_inputs.keys())
        
        # Validasi positif (Harus ada)
        for g_kode in ekspektasi_mengandung:
            if g_kode in gejala_terdeteksi:
                print(f"[PASS] Gejala {g_kode} terdeteksi.")
                passed += 1
            else:
                print(f"[FAIL] Gejala {g_kode} SEHARUSNYA terdeteksi namun hilang.")
                failed += 1
                
        # Validasi negatif (Tidak Boleh ada)
        for g_kode in ekspektasi_TIDAK_mengandung:
            if g_kode in gejala_terdeteksi:
                print(f"[FAIL] Gejala {g_kode} TERDETEKSI (Padahal sudah dinegasi/tidak relevan).")
                failed += 1
            else:
                print(f"[PASS] Gejala {g_kode} berhasil diabaikan/tidak ada.")
                passed += 1

    total = passed + failed
    status = "LULUS" if failed == 0 else "GAGAL"
    
    return {
        "Skenario": nama_skenario.split(":")[0], 
        "Status": status, 
        "Pass": passed, 
        "Fail": failed, 
        "Total": total
    }

def main():
    results = []
    
    # Skenario 1: Kasus Normal
    results.append(run_test(
        "SKENARIO 1: Kasus Ideal (Kalimat Jelas)",
        "aku sering sakit kepala banget dan akhir-akhir ini sulit tidur",
        ekspektasi_mengandung=["G09", "G10"],
        ekspektasi_TIDAK_mengandung=[]
    ))
    
    # Skenario 2: Kasus Negasi
    results.append(run_test(
        "SKENARIO 2: Logika Negasi (Tidak / Bukan)",
        "saya tidak pusing dan gak susah tidur, tapi nafas agak sesak",
        ekspektasi_mengandung=["G01"],
        ekspektasi_TIDAK_mengandung=["G09", "G10"]
    ))
    
    # Skenario 3: Kasus Slang
    results.append(run_test(
        "SKENARIO 3: Bahasa Gaul, Angka, & Kapitalisasi Acak",
        "aku tu akhir2 ini sering banget SUSAH tidur... trus dada suka berdebar gajelas gitu.",
        ekspektasi_mengandung=["G10", "G02"],
        ekspektasi_TIDAK_mengandung=[]
    ))

    # Skenario 4: Paragraf Panjang
    results.append(run_test(
        "SKENARIO 4: Paragraf Panjang Curhatan",
        "Halo dok, perkenalkan saya Budi. Saya akhir-akhir ini tuh merasa gampang capek setiap habis kerja. Terus yang paling mengganggu itu SAKIT KEPALA banget gatau kenapa padahal udah istirahat cukup. Trus ya gitu dehhh... nafasku kadang suka sesak padahal nggak ada riwayat asma atau alergi debu. Terus malamnya itu sumpah SUSAH banget buat tidur nyenyak. Kira-kira saya sakit apa ya dok?",
        ekspektasi_mengandung=["G09", "G10", "G01"],
        ekspektasi_TIDAK_mengandung=[]
    ))
    
    # Skenario 5: Tanda Baca
    results.append(run_test(
        "SKENARIO 5: Tanda Baca Berantakan dan Campur Kapitalisasi",
        "dok...tolong,,,dada,,suka,,BERDEBAR-DEBAR gajelas?!, pdhl tdk pusing...tp sulit...tidur. knp ya dok???!!",
        ekspektasi_mengandung=["G02", "G10"],
        ekspektasi_TIDAK_mengandung=["G09"]
    ))
    
    # Skenario 6: Multiple Negation
    results.append(run_test(
        "SKENARIO 6: Multi-Negasi di Kalimat Kompleks",
        "hari ini saya tidak sesak nafas dan bukan pusing, cuma agak susah tidur aja",
        ekspektasi_mengandung=["G10"],
        ekspektasi_TIDAK_mengandung=["G01", "G09"]
    ))

    # Skenario 7: Typo Parah
    results.append(run_test(
        "SKENARIO 7: Typo Parah (Salah Ketik)",
        "dok kpla sya pusiiing bnget trs mual2 gtu, nafas jg sesek.",
        ekspektasi_mengandung=["G09", "G01"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 8: Sinonim Khusus
    results.append(run_test(
        "SKENARIO 8: Kata Kiasan / Bahasa Gaul / Sinonim",
        "perut saya rasanya eneg, kepala mumet banget muter-muter, terus dada deg-degan.",
        ekspektasi_mengandung=["G09", "G02"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 9: Negasi Jarak Jauh
    results.append(run_test(
        "SKENARIO 9: Negasi Jarak Jauh (Long-Distance Negation)",
        "saya tidak pernah merasa dada saya itu berdebar dok.",
        ekspektasi_mengandung=[], 
        ekspektasi_TIDAK_mengandung=["G02"]
    ))

    # Skenario 10: Kontradiksi
    results.append(run_test(
        "SKENARIO 10: Kontradiksi Waktu (Dulu vs Sekarang)",
        "seminggu lalu emang pusing, tapi sekarang udah nggak pusing lagi, cuma tinggal susah tidur aja.",
        ekspektasi_mengandung=["G10"],
        ekspektasi_TIDAK_mengandung=["G09"]
    ))

    # Skenario 11: Pemisahan Gejala
    results.append(run_test(
        "SKENARIO 11: Pemisahan Gejala Bertumpuk Tanpa Spasi",
        "sakitkepala banget dok, trus dada.berdebar.",
        ekspektasi_mengandung=["G09", "G02"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 12: Pengulangan Gejala Berkali-kali
    results.append(run_test(
        "SKENARIO 12: Pengulangan Kata Gejala Berlebihan",
        "pusing pusing pusing banget nih dok, kepala rasanya pusing.",
        ekspektasi_mengandung=["G09"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 13: Fuzzy Typo disertai Negasi Konteks
    results.append(run_test(
        "SKENARIO 13: Fuzzy Typo + Negasi",
        "saya sebenernya nggk puuusiing kok, cuma agak seseeek nafas aja.",
        ekspektasi_mengandung=["G01"], # seseeek -> sesak
        ekspektasi_TIDAK_mengandung=["G09"] # nggk puuusiing -> diabaikan
    ))

    # Skenario 14: Kalimat Pertanyaan
    results.append(run_test(
        "SKENARIO 14: Kalimat Pertanyaan",
        "halo dok, apakah normal kalau akhir-akhir ini saya selalu merasa susah tidur ya?",
        ekspektasi_mengandung=["G10"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 15: Tanda Baca Simbol Ekstrem
    results.append(run_test(
        "SKENARIO 15: Tanda Baca / Simbol Ekstrem",
        "aduhhh @#$sakit*&kepala!! banget dan sEsAK%^&* nafas",
        ekspektasi_mengandung=["G09", "G01"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 16: Spasi Kosong / Terlalu Banyak
    results.append(run_test(
        "SKENARIO 16: Kelebihan Spasi",
        "saya      merasa        pusing      dan   dada     berdebar",
        ekspektasi_mengandung=["G09", "G02"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 17: Typo Campur Karakter Angka Alay
    results.append(run_test(
        "SKENARIO 17: Typo Alay (Karakter + Angka)",
        "s4kit k3pala b4nget dok, susah tidurr",
        ekspektasi_mengandung=["G10"], # susah tidurr -> G10. (s4kit k3pala mungkin lolos fuzzy/gagal)
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 18: Negasi dengan Konteks Panjang
    results.append(run_test(
        "SKENARIO 18: Negasi Super Jauh (10+ Kata)",
        "saya sama sekali tidak pernah memiliki riwayat penyakit sesak nafas dok.",
        ekspektasi_mengandung=[],
        ekspektasi_TIDAK_mengandung=["G01"] # sesak nafas harus ditolak
    ))

    # Skenario 19: Gejala Pendek Fuzzy Bawah Ambang (Anti-False Positive)
    results.append(run_test(
        "SKENARIO 19: Kata Mirip tapi Beda Makna",
        "cuaca hari ini sangat panas ya dok.",
        ekspektasi_mengandung=[],
        ekspektasi_TIDAK_mengandung=["G01"] # "panas" mirip "nafas", harusnya ditolak karena beda makna
    ))

    # Skenario 20: Kesimpulan Gejala
    results.append(run_test(
        "SKENARIO 20: Deskripsi Singkat Padat",
        "pusing, mual, susah tidur",
        ekspektasi_mengandung=["G09", "G04", "G10"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 21: Penggunaan Emoji (Teks Tercampur)
    results.append(run_test(
        "SKENARIO 21: Emoji dan Emotikon",
        "aduh kepalaku pusing banget T_T, rasanya mual x_x",
        ekspektasi_mengandung=["G09", "G04"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 22: Campuran Bahasa Inggris (Slang/Jaksel)
    results.append(run_test(
        "SKENARIO 22: Bahasa Campur / Slang Inggris",
        "literally pusing banget today dok, totally gak bisa tidur",
        ekspektasi_mengandung=["G09"],
        ekspektasi_TIDAK_mengandung=["G10"] # 'gak' membatalkan 'tidur'
    ))

    # Skenario 23: Input Super Pendek (Satu Kata)
    results.append(run_test(
        "SKENARIO 23: Input Satu Kata Saja",
        "mual",
        ekspektasi_mengandung=["G04"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 24: Huruf Kapital Semua (Yelling)
    results.append(run_test(
        "SKENARIO 24: Huruf Kapital (All Caps)",
        "SUSAH TIDUR DARI KEMARIN DOK TOLONG SAYA SESAK",
        ekspektasi_mengandung=["G10", "G01"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 25: Konteks Medis Ekstra (Irrelevan)
    results.append(run_test(
        "SKENARIO 25: Konteks Medis Ekstra (Noise)",
        "saya habis operasi usus buntu bulan lalu, tapi sekarang keluhannya cuma mual aja.",
        ekspektasi_mengandung=["G04"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 26: Typo pada Kata Negasi
    results.append(run_test(
        "SKENARIO 26: Typo Ekstrem di Kata Negasi",
        "saya sebenernya nggakkk pusing dok.",
        ekspektasi_mengandung=[],
        ekspektasi_TIDAK_mengandung=["G09"] # Harusnya diabaikan, tapi 'nggakkk' mungkin blm ada di kamus negasi
    ))

    # Skenario 27: Pengulangan Karakter di Akhir Kata (Spam Huruf)
    results.append(run_test(
        "SKENARIO 27: Spam Huruf / Tarikan Kata",
        "pusinggggggg bangettttttttt dokkkk",
        ekspektasi_mengandung=["G09"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 28: Kalimat Kontradiktif Ganda (Konteks Waktu)
    results.append(run_test(
        "SKENARIO 28: Kalimat Kontradiktif Lintas Kalimat",
        "kemarin sih dada berdebar. tapi hari ini udah sembuh dan gak berdebar lagi.",
        ekspektasi_mengandung=["G02"], # Terdeteksi di kalimat pertama
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 29: Gejala Berurutan Cepat
    results.append(run_test(
        "SKENARIO 29: Rentetan Gejala Beruntun",
        "pusing dan mual terus sesak nafas",
        ekspektasi_mengandung=["G09", "G04", "G01"],
        ekspektasi_TIDAK_mengandung=[] 
    ))

    # Skenario 30: Teks Kosong / Tanpa Makna
    results.append(run_test(
        "SKENARIO 30: Input Tanpa Makna Tersembunyi (Angka/Simbol Semata)",
        "12345 !@#$% ^&*()",
        ekspektasi_mengandung=[],
        ekspektasi_TIDAK_mengandung=["G01", "G02", "G04", "G09", "G10"] 
    ))

    print("\n\n" + "="*65)
    print(" "*18 + "HASIL PENGUJIAN NLP" + " "*18)
    print("="*65)
    print(f"| {'Skenario':<15} | {'Status':<10} | {'Pass':<5} | {'Fail':<5} | {'Total':<5} |")
    print("-" * 65)
    
    total_scenarios = len(results)
    passed_scenarios = 0
    
    for r in results:
        if r['Fail'] == 0:
            passed_scenarios += 1
            status_text = f"LULUS"
        else:
            status_text = f"GAGAL"
        print(f"| {r['Skenario']:<15} | {status_text:<10} | {r['Pass']:<5} | {r['Fail']:<5} | {r['Total']:<5} |")
        
    print("-" * 65)
    
    print("\n GRAFIK TINGKAT KEBERHASILAN SKENARIO")
    print("-" * 65)
    for r in results:
        # Gunakan karakter ASCII standar agar aman di semua terminal
        pass_bars = "O" * r['Pass']
        fail_bars = "X" * r['Fail']
        print(f"{r['Skenario']:<15} | {pass_bars}{fail_bars} ({r['Pass']}/{r['Total']})")

    print("-" * 65)
    accuracy = (passed_scenarios / total_scenarios) * 100
    print(f" AKURASI KESELURUHAN: {accuracy:.1f}% ({passed_scenarios}/{total_scenarios} Skenario Lulus)")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
