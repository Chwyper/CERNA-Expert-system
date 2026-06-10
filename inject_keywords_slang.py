"""
Script untuk menambahkan keyword casual/gaul/slang Indonesia
ke dalam database KataKunci. Hanya menambahkan yang belum ada (skip duplikat).
"""
from app import app
from models import db, KataKunci

TAMBAHAN_KEYWORDS = {
    # ── GEJALA FISIK / SOMATIK ────────────────────────────────────
    "G01": [  # Sering napas pendek
        ("terengah", 0.8), ("nafas seret", 0.85), ("dada sesek", 0.85),
        ("gak bisa napas", 0.9), ("napas kayak ikan", 0.8),
    ],
    "G02": [  # Nadi dan tekanan darah naik
        ("jantung mau copot", 0.85), ("berasa deg-degan", 0.8), ("jantung kayak drum", 0.8),
        ("deg degan", 0.8), ("bergetar", 0.75),
    ],
    "G03": [  # Mulut kering
        ("tenggorokan seret", 0.85), ("mulut kayak pasir", 0.8), ("minum terus", 0.75),
        ("kerongkongan kering", 0.85), ("nyaris gak ada liur", 0.8),
    ],
    "G04": [  # Anoreksia / tidak nafsu makan
        ("gak doyan makan", 0.85), ("males ngunyah", 0.8), ("gak pengen makan", 0.85),
        ("liat makanan males", 0.8), ("gak kuat makan", 0.8),
    ],
    "G09": [  # Sakit kepala berulang
        ("kepala mau pecah", 0.85), ("migrain", 0.9), ("pala berat", 0.85),
        ("kepala mumet", 0.85), ("pusing tujuh keliling", 0.8),
    ],
    "G10": [  # Sulit tidur / insomnia
        ("susah pejam mata", 0.85), ("rebahan gak bisa bobo", 0.85),
        ("kejar tidur gak ketemu", 0.8), ("mata melek mulu", 0.85), ("gak ngantuk-ngantuk", 0.8),
    ],
    "G11": [  # Berkeringat berlebih
        ("schwetty banget", 0.75), ("basah kuyup padahal ac", 0.8), ("keringetan gak kira-kira", 0.8),
        ("peluh terus", 0.8), ("awet basah", 0.75),
    ],

    # ── PSIKOLOGIS / EMOSI ────────────────────────────────────────
    "G12": [  # Merasa tidak bisa mengendalikan situasi
        ("kacau banget", 0.8), ("gak ada yang bisa aku kontrol", 0.85),
        ("semua lepas", 0.8), ("gak berdaya banget", 0.85), ("overwhelmed parah", 0.85),
    ],
    "G13": [  # Merasa tidak produktif
        ("gak ada capainya", 0.8), ("makan aja gak berguna", 0.8),
        ("gak ada kontribusi", 0.8), ("nganggur jiwa raga", 0.75), ("zero produktivitas", 0.8),
    ],
    "G14": [  # Frustrasi
        ("frustrasi banget", 0.9), ("nyesel banget", 0.8), ("dongkol", 0.85),
        ("emosi jiwa", 0.85), ("kesal abis", 0.85),
    ],
    "G15": [  # Ragu-ragu akan peran diri
        ("gak tau gue itu siapa", 0.85), ("lost identity", 0.85),
        ("gak ada pegangan", 0.8), ("hidup gak jelas", 0.8), ("crisis identitas", 0.85),
    ],
    "G19": [  # Enggan ungkapkan perasaan
        ("gak bisa terbuka", 0.85), ("nemenin masalah sendiri", 0.8),
        ("nutup diri rapet", 0.85), ("diem aja soal perasaan", 0.85), ("keep it to myself", 0.8),
    ],
    "G20": [  # Ketergantungan + iritabilitas
        ("mudah banget meledak", 0.85), ("gampang gerah", 0.8),
        ("cepet nyolot", 0.85), ("nempel mulu terus ngehina", 0.8), ("kecil-kecil meledak", 0.8),
    ],

    # ── SOSIAL / INTERPERSONAL ────────────────────────────────────
    "G27": [  # Aktivitas sosial menurun
        ("jarang nongkrong", 0.85), ("cabut dari circle", 0.85),
        ("hilangin diri", 0.8), ("gak muncul-muncul", 0.85), ("ngilang dari radar", 0.85),
    ],
    "G30": [  # Sering ucapkan hal negatif tentang diri
        ("jelek-jelekin diri sendiri", 0.85), ("ngehina diri terus", 0.85),
        ("self roasting terus", 0.8), ("nyalahin diri sendiri mulu", 0.85), ("gue emang payah", 0.85),
    ],
    "G31": [  # Susah ambil keputusan sehari-hari
        ("galau mulu", 0.85), ("takut salah terus", 0.85),
        ("gak bisa milih", 0.85), ("beli mie aja dipikir seharian", 0.8), ("otaknya ngehang", 0.8),
    ],
    "G33": [  # Ucapkan hal negatif tentang diri
        ("selalu ngerasa gak bisa", 0.85), ("ngeluh mulu", 0.8),
        ("sambat terus", 0.8), ("pesimis parah", 0.85), ("self-deprecating terus", 0.8),
    ],
    "G36": [  # Hidup terasa hampa
        ("hampa banget", 0.9), ("ngerasa kosong di dalam", 0.9),
        ("gak ada tujuan hidup", 0.9), ("buat apa hidup", 0.9), ("void", 0.85),
    ],

    # ── GEJALA PSIKOTIK / MANIA ───────────────────────────────────
    "G43": [  # Dengar bisikan
        ("denger suara random", 0.85), ("ada yang manggil tapi gak ada", 0.85),
        ("kepala rame sendiri", 0.8), ("ada suara di kepala", 0.9), ("ngedenger tapi sepi", 0.85),
    ],
    "G44": [  # Lihat bayangan
        ("ngeliat sesuatu yang gak ada orangnya", 0.85), ("ada yang keliatan", 0.8),
        ("ngeliat sosok", 0.85), ("sesuatu melintas", 0.8), ("matanya maen sendiri", 0.75),
    ],
    "G46": [  # Mondar-mandir gelisah
        ("bolak balik gak jelas", 0.85), ("gak bisa anteng", 0.85),
        ("resah gak karuan", 0.85), ("duduk sebentar terus gerak lagi", 0.8), ("kayak setrum", 0.75),
    ],
    "G48": [  # Konsentrasi buruk
        ("gak bisa mikir jernih", 0.85), ("otak lemot", 0.8),
        ("gampang distraksi", 0.85), ("buyar terus", 0.85), ("gak nyambung ngomongnya", 0.8),
    ],
    "G49": [  # Delusi / keyakinan ganjil
        ("ngaku-ngaku jadi orang penting", 0.9), ("ngerasa dipilih tuhan", 0.9),
        ("yakin hal absurd", 0.85), ("ngomong hal gak masuk akal", 0.85), ("ngerasa istimewa banget", 0.8),
    ],
    "G50": [  # Curiga berlebihan
        ("parno abis", 0.9), ("ngerasa ditungguin", 0.85),
        ("curiga semua orang", 0.9), ("gak percaya siapapun", 0.85), ("ngerasa dimata-matai", 0.9),
    ],
    "G51": [  # Bicara loncat-loncat topik
        ("ngomong gak nyambung", 0.85), ("cerita random mulu", 0.8),
        ("loncat topik mulu", 0.85), ("obrolan gak jelas", 0.8), ("ngelantur terus", 0.85),
    ],
    "G74": [  # Euforia mendadak
        ("tiba-tiba happy banget", 0.9), ("energi meledak tiba-tiba", 0.85),
        ("gak normal senengnya", 0.85), ("bahagia gak wajar", 0.85), ("heboh sendiri", 0.8),
    ],

    # ── SUICIDAL / KRISIS ─────────────────────────────────────────
    "G36": [  # Hampa / hopeless
        ("gak ada yang nunggu", 0.9), ("capek banget hidup", 0.9),
        ("buat apa ada", 0.9), ("ngerasa sendiri banget", 0.85), ("dunia terasa gelap", 0.9),
    ],
    "G71": [  # Ingin akhiri hidup
        ("pengen pergi selamanya", 0.95), ("capek hidup", 0.95),
        ("pengen gak ada", 0.95), ("gak pengen bangun lagi", 0.95), ("mati aja deh", 0.95),
    ],
    "G75": [  # Merasa jadi beban
        ("ngerasa nyusahin orang", 0.9), ("mending aku ilang", 0.95),
        ("semua lebih baik tanpa aku", 0.95), ("ganggu hidup orang", 0.9), ("gak diperlukan", 0.9),
    ],

    # ── PERAWATAN DIRI / HIGIENITAS ───────────────────────────────
    "G66": [  # Malas mandi
        ("malas bersih-bersih", 0.85), ("gak sempet mandi", 0.8),
        ("cuek sama kebersihan", 0.85), ("gak ingat terakhir mandi", 0.85), ("skip shower", 0.85),
    ],
    "G67": [  # Rambut/gigi kotor
        ("penampilan gak keurus", 0.85), ("badan bau aja gapapa", 0.8),
        ("rambut lepek gak peduli", 0.8), ("gigi gak disikat", 0.85), ("jorok males ngurus", 0.85),
    ],
    "G42": [  # Pasif / tidak semangat
        ("lesu banget", 0.85), ("gak ada gairah", 0.85),
        ("dead inside", 0.9), ("hidup autopilot", 0.85), ("zombie mode on", 0.85),
    ],

    # ── CITRA TUBUH ──────────────────────────────────────────────
    "G28": [  # Malu/bersalah soal tubuh
        ("gak suka badan sendiri", 0.85), ("minder sama fisik", 0.85),
        ("ngerasa jelek banget", 0.85), ("ngehina fisik sendiri", 0.85), ("body shame", 0.9),
    ],
    "G61": [  # Menilai diri negatif kronis
        ("ngerasa paling gak berguna", 0.9), ("hidup percuma", 0.9),
        ("gak ada yang perlu aku", 0.9), ("gak ada nilainya", 0.9), ("mati pun gak ada yang kehilangan", 0.95),
    ],
}

def inject_keywords():
    with app.app_context():
        added = 0
        skipped = 0

        for g_kode, keywords in TAMBAHAN_KEYWORDS.items():
            for kata, bobot in keywords:
                kata_lower = kata.lower().strip()
                exists = KataKunci.query.filter_by(gejala_kode=g_kode, kata=kata_lower).first()
                if exists:
                    skipped += 1
                    continue
                kw = KataKunci(gejala_kode=g_kode, kata=kata_lower, bobot=bobot)
                db.session.add(kw)
                added += 1

        db.session.commit()
        print(f"[SUCCESS] Selesai! {added} kata kunci baru ditambahkan, {skipped} kata duplikat dilewati.")

if __name__ == "__main__":
    inject_keywords()
