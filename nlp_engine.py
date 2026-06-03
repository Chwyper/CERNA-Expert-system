# pyrefly: ignore [missing-import]
import saka
from sqlalchemy import or_
from models import KataKunci

def proses_pesan_chatbot(teks_pesan):
    """
    Mengurai teks mentah (curhatan) pengguna menjadi kamus probabilitas gejala (user_inputs)
    yang kompatibel dengan algoritma Certainty Factor lama kita.
    
    Alur: Normalisasi Slang -> Tokenisasi -> Hapus Stopword -> Cari Akar Kata -> Cocokkan ke DB.
    """
    
    # 1. Slang Normalization & Cleansing (Menerjemahkan bahasa gaul)
    # Contoh: "aku lg males bgt" -> "saya sedang malas banget"
    teks_normal = saka.normalize(teks_pesan.lower())
    print(f"[NLP] Teks Ternormalisasi: {teks_normal}")
    
    # 2. Tokenization (Memecah menjadi deretan kata)
    tokens = saka.tokenize(teks_normal)
    print(f"[NLP] Tokens Asli: {tokens}")
    
    # 3. Mendefinisikan Stopwords dan Kata Negasi
    stopwords_id = saka.get_stopwords('id')
    kata_negasi = ["tidak", "bukan", "kurang", "gak", "enggak", "ndak", "nggak", "belum", "belom"]
    
    user_inputs = {}
    kata_dikenali = []
    
    # 4. Heuristic Morphology, Negation Checking & Matching
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
            
        # B. Filter Stopword (Hanya jika bukan negasi yang ke-skip)
        if token in stopwords_id:
            continue
            
        # C. Mencari bentuk akar dari kata tersebut
        hasil_analisis = saka.analyze(token)
        akar_kata = hasil_analisis.get("root", token)
        
        # D. Database Lookup (Mencocokkan ke database menggunakan token ATAU akar_kata)
        keywords = KataKunci.query.filter(or_(KataKunci.kata == akar_kata, KataKunci.kata == token)).all()
        
        for kw in keywords:
            g_kode = kw.gejala_kode
            bobot = kw.bobot
            kata_dikenali.append(kw.kata) # Menyimpan kata yang benar-benar cocok
            
            # Jika satu gejala terdeteksi dari beberapa kata, ambil bobot teringgi
            if g_kode in user_inputs:
                user_inputs[g_kode] = max(user_inputs[g_kode], bobot)
            else:
                user_inputs[g_kode] = bobot
                
    print(f"[NLP] Akar Kata Terdeteksi di DB: {list(set(kata_dikenali))}")
    print(f"[NLP] Hasil Konversi (user_inputs): {user_inputs}")
    
    return user_inputs
