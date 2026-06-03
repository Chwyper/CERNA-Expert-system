# pyrefly: ignore [missing-import]
import saka
from sqlalchemy import or_
from models import KataKunci

def proses_pesan_chatbot(teks_pesan):
    """
    Mengurai teks mentah (curhatan) pengguna menjadi kamus probabilitas gejala (user_inputs)
    yang kompatibel dengan algoritma Certainty Factor lama kita.
    
    Alur BARU: Normalisasi Slang -> PENCARIAN FRASE UTUH -> Tokenisasi Kata Tunggal -> Cocokkan ke DB.
    """
    if not teks_pesan:
        return {}

    # 1. Slang Normalization & Cleansing (Menerjemahkan bahasa gaul)
    teks_normal = saka.normalize(teks_pesan.lower())
    print(f"[NLP] Teks Ternormalisasi: {teks_normal}")
    
    user_inputs = {}
    kata_dikenali = []

    # =========================================================================
    # ── LOGIKA BARU: PENCARIAN FRASE UTUH (AGAR CHATBOT AUTO PINTAR)
    # Langkah ini mencari frase gaul panjang (misal: "ga nafsu makan", "deg-degan") 
    # langsung di dalam kalimat utuh sebelum dipotong-potong oleh tokenisasi.
    # =========================================================================
    try:
        # Ambil semua kata kunci dari database untuk dicocokkan secara fleksibel
        semua_keyword_db = KataKunci.query.all()
        for kw in semua_keyword_db:
            kata_kunci_db = kw.kata.lower().strip()
            
            # Jika kata/frase dari DB ternyata tertulis di dalam curhatan user
            if kata_kunci_db in teks_normal:
                g_kode = kw.gejala_kode
                bobot = kw.bobot
                kata_dikenali.append(kw.kata)
                
                # Masukkan ke user_inputs, ambil bobot tertinggi jika ada yang kembar
                if g_kode in user_inputs:
                    user_inputs[g_kode] = max(user_inputs[g_kode], bobot)
                else:
                    user_inputs[g_kode] = bobot
    except Exception as e:
        print(f"[NLP Error] Gagal mencocokkan frase utuh: {e}")
    # =========================================================================

    # 2. Tokenization (Tetap jalankan fitur bawaan tim kamu untuk kata tunggal)
    tokens = saka.tokenize(teks_normal)
    print(f"[NLP] Tokens Asli: {tokens}")
    
    # 3. Mendefinisikan Stopwords dan Kata Negasi
    stopwords_id = saka.get_stopwords('id')
    kata_negasi = ["tidak", "bukan", "kurang", "gak", "enggak", "ndak", "nggak", "belum", "belom"]
    
    # 4. Heuristic Morphology, Negation Checking & Matching (Fitur Asli Tim)
    for i, token in enumerate(tokens):
        # A. Cek Negasi (Melihat 1 atau 2 kata sebelumnya)
        is_negated = False
        if i > 0 and tokens[i-1] in kata_negasi:
            is_negated = True
        elif i > 1 and tokens[i-2] in kata_negasi:
            is_negated = True
            
        if is_negated:
            print(f"[NLP] Kata '{token}' DIABAIKAN (Terdeteksi Negasi)")
            continue  # Lewati kata ini sepenuhnya
            
        # B. Filter Stopword
        if token in stopwords_id:
            continue
            
        # C. Mencari bentuk akar dari kata tersebut
        hasil_analisis = saka.analyze(token)
        akar_kata = hasil_analisis.get("root", token)
        
        # D. Database Lookup untuk Kata Tunggal (Jika belum ketangkap di pencarian frase atas)
        keywords = KataKunci.query.filter(or_(KataKunci.kata == akar_kata, KataKunci.kata == token)).all()
        
        for kw in keywords:
            g_kode = kw.gejala_kode
            bobot = kw.bobot
            
            if g_kode not in user_inputs:
                kata_dikenali.append(kw.kata)
                user_inputs[g_kode] = bobot
            else:
                user_inputs[g_kode] = max(user_inputs[g_kode], bobot)
                
    print(f"[NLP] Akar Kata/Frase Terdeteksi di DB: {list(set(kata_dikenali))}")
    print(f"[NLP] Hasil Konversi Akhir (user_inputs): {user_inputs}")
    
    return user_inputs