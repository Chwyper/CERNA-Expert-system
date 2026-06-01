import saka
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
    
    # 3. Stopword Removal (Membuang kata hubung/tidak penting)
    stopwords_id = saka.get_stopwords('id')
    filtered_tokens = [t for t in tokens if t not in stopwords_id]
    
    user_inputs = {}
    kata_dikenali = []
    
    # 4. Heuristic Morphology & Matching (Stemming dan pencocokan ke database)
    for token in filtered_tokens:
        # Mencari bentuk akar dari kata tersebut
        hasil_analisis = saka.analyze(token)
        akar_kata = hasil_analisis.get("root", token)
        
        # 5. Database Lookup (Mencari apakah akar kata ini ada di kamus gejala kita)
        keywords = KataKunci.query.filter_by(kata=akar_kata).all()
        
        for kw in keywords:
            g_kode = kw.gejala_kode
            bobot = kw.bobot
            kata_dikenali.append(akar_kata)
            
            # Jika satu gejala terdeteksi dari beberapa kata, ambil bobot teringgi
            if g_kode in user_inputs:
                user_inputs[g_kode] = max(user_inputs[g_kode], bobot)
            else:
                user_inputs[g_kode] = bobot
                
    print(f"[NLP] Akar Kata Terdeteksi di DB: {list(set(kata_dikenali))}")
    print(f"[NLP] Hasil Konversi (user_inputs): {user_inputs}")
    
    return user_inputs
