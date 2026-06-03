# pyrefly: ignore [missing-import]
import saka
from sqlalchemy import or_
from models import KataKunci
from difflib import SequenceMatcher

# ── In-memory cache untuk kata kunci NLP ─────────────────────────────────────
# Cache di-load sekali dari DB, dan di-invalidate saat admin mengubah kata kunci.
_keyword_cache = None

def get_keywords():
    """Mengembalikan daftar kata kunci dari cache. Query DB jika cache kosong."""
    global _keyword_cache
    if _keyword_cache is None:
        _keyword_cache = KataKunci.query.all()
        print(f"[NLP Cache] Keyword cache dimuat: {len(_keyword_cache)} entri")
    return _keyword_cache

def invalidate_keyword_cache():
    """Menghapus cache agar di-refresh dari DB pada request berikutnya."""
    global _keyword_cache
    _keyword_cache = None
    print("[NLP Cache] Cache kata kunci di-invalidate.")

def is_negated_in_context(teks_normal, match_start, kata_negasi):
    """
    Memeriksa apakah ada kata negasi sebelum kata kunci yang ditemukan.
    Pencarian mundur sampai menemukan batas konteks (tanda baca atau konjungsi).
    """
    text_before = teks_normal[:match_start].strip()
    if not text_before:
        return False
        
    words = text_before.split()
    batas_konteks = [".", ",", "?", "!", ";", "tapi", "tetapi", "dan", "lalu", "kemudian", "namun", "sedangkan", "meskipun"]
    
    konteks_terdekat = []
    for w in reversed(words):
        if w in batas_konteks:
            break
        konteks_terdekat.append(w)
        
    return any(w in kata_negasi for w in konteks_terdekat)

def cari_keyword_fuzzy(token, semua_keyword_db, threshold=0.75):
    """
    Mencari kata kunci dari database yang mirip dengan token menggunakan
    SequenceMatcher (setara Levenshtein). Hanya memproses token > 4 huruf.
    """
    kandidat = []
    if len(token) <= 4:
        return kandidat
        
    for kw in semua_keyword_db:
        kata_db = kw.kata.lower().strip()
        if ' ' in kata_db:
            continue
            
        # Fast fail: beda panjang lebih dari 40% pasti di bawah threshold
        if abs(len(kata_db) - len(token)) > max(len(kata_db), len(token)) * 0.4:
            continue
            
        kemiripan = SequenceMatcher(None, token, kata_db).ratio()
        if kemiripan >= threshold:
            kandidat.append((kw, kemiripan))
            
    return sorted(kandidat, key=lambda x: x[1], reverse=True)

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

    # Kata-kata yang menandakan penolakan atau ketiadaan gejala (termasuk typo)
    kata_negasi = {
        "tidak", "bukan", "kurang", "gak", "enggak", "ndak", "nggak", "belum", "belom", "tdk", "ngga", "gk",
        "nggk", "nggakk", "nggakkk", "kaga", "kagak", "nda", "tak", "jangan"
    }
    
    # =========================================================================
    # ── LOGIKA BARU: PENCARIAN FRASE UTUH (AGAR CHATBOT AUTO PINTAR)
    # =========================================================================
    try:
        import re
        semua_keyword_db = get_keywords()
        for kw in semua_keyword_db:
            kata_kunci_db = kw.kata.lower().strip()
            
            # Cari menggunakan Regex agar batas kata akurat dan mendapat indeks (start)
            pattern = r'(?<!\w)' + re.escape(kata_kunci_db) + r'(?!\w)'
            matches = list(re.finditer(pattern, teks_normal))
            
            for match in matches:
                # Cek Negasi Jarak Jauh
                if is_negated_in_context(teks_normal, match.start(), kata_negasi):
                    print(f"[NLP] Frase '{kata_kunci_db}' DIABAIKAN (Terdeteksi Negasi Konteks)")
                    continue
                    
                g_kode = kw.gejala_kode
                bobot = kw.bobot
                kata_dikenali.append(kw.kata)
                
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
    
    # 3. Mendefinisikan Stopwords
    stopwords_id = saka.get_stopwords('id')
    
    # Hitung akumulasi panjang string untuk mencari index token asli di teks_normal
    current_index = 0
    
    # 4. Heuristic Morphology & Matching (Fitur Asli Tim yang Disempurnakan)
    for token in tokens:
        # Cari start index dari token ini di teks_normal
        token_start = teks_normal.find(token, current_index)
        if token_start != -1:
            current_index = token_start + len(token)
        else:
            token_start = current_index
            
        # A. Cek Negasi dengan Konteks
        if is_negated_in_context(teks_normal, token_start, kata_negasi):
            print(f"[NLP] Kata '{token}' DIABAIKAN (Terdeteksi Negasi Konteks)")
            continue  # Lewati kata ini sepenuhnya

            
        # B. Filter Stopword
        if token in stopwords_id:
            continue
            
        # C. Mencari bentuk akar dari kata tersebut
        hasil_analisis = saka.analyze(token)
        akar_kata = hasil_analisis.get("root", token)
        
        # D. Database Lookup untuk Kata Tunggal (Eksak)
        keywords = KataKunci.query.filter(or_(KataKunci.kata == akar_kata, KataKunci.kata == token)).all()
        
        # E. Coba Fuzzy Matching jika pencarian eksak gagal
        if not keywords:
            semua_keyword_db = get_keywords()
            fuzzy_results = cari_keyword_fuzzy(token, semua_keyword_db, threshold=0.75)
            if fuzzy_results:
                kw_terbaik, skor = fuzzy_results[0]
                print(f"[NLP Fuzzy] '{token}' ~= '{kw_terbaik.kata}' (skor: {skor:.2f})")
                
                g_kode = kw_terbaik.gejala_kode
                bobot_fuzzy = kw_terbaik.bobot * skor # Beri penalti keyakinan sesuai skor kemiripan
                
                if g_kode not in user_inputs:
                    kata_dikenali.append(f"{token}~={kw_terbaik.kata}")
                    user_inputs[g_kode] = bobot_fuzzy
                else:
                    user_inputs[g_kode] = max(user_inputs[g_kode], bobot_fuzzy)
                continue # Lanjut ke token berikutnya
        
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