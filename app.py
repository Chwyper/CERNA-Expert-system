"""
CERNA v2.0 — Sistem Pakar Diagnosa Kesehatan Mental
Enhanced Flask App:
  - Kategori penyakit (pilih dulu sebelum asesmen)
  - Deskripsi & rekomendasi detail per penyakit
  - Halaman Admin dengan CRUD Knowledge Base
  - Autentikasi admin sederhana via session
"""

# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json, os, copy

app = Flask(__name__)
app.secret_key = "cerna_secret_2026"   # Ganti dengan nilai random di produksi

# ──────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE (data diperluas dengan deskripsi & rekomendasi detail)
# ──────────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = {
    "P01": {
        "nama_penyakit": "ANSIETAS",
        "kategori": "mood",
        "deskripsi": (
            "Ansietas (kecemasan) adalah kondisi di mana seseorang mengalami perasaan khawatir, "
            "takut, atau gelisah yang berlebihan terhadap situasi yang mungkin terjadi. "
            "Berbeda dengan rasa takut biasa, ansietas cenderung persisten dan dapat mengganggu "
            "aktivitas sehari-hari, pekerjaan, serta hubungan sosial. "
            "Gejalanya mencakup reaksi fisik seperti jantung berdebar, keringat berlebih, "
            "sesak napas, dan reaksi psikologis seperti pikiran yang terus berputar."
        ),
        "gejala": {
            "G01": {"nama": "Sering napas pendek",                 "cf_pakar": 0.90},
            "G02": {"nama": "Nadi dan tekanan darah naik",         "cf_pakar": 0.95},
            "G03": {"nama": "Mulut kering",                        "cf_pakar": 0.90},
            "G04": {"nama": "Anoreksia (tidak nafsu makan)",       "cf_pakar": 0.91},
            "G09": {"nama": "Sakit kepala berulang",               "cf_pakar": 0.92},
            "G10": {"nama": "Sulit tidur / insomnia",              "cf_pakar": 0.96},
            "G11": {"nama": "Berkeringat berlebih",                "cf_pakar": 0.98},
        },
        "rekomendasi": {
            "ringkas": "Teknik relaksasi dan manajemen stres",
            "detail": [
                "Latihan napas dalam (diaphragmatic breathing) selama 5–10 menit, 2× sehari.",
                "Teknik relaksasi otot progresif (PMR) sebelum tidur untuk mengurangi ketegangan fisik.",
                "Journaling harian: tulis pemicu kecemasan dan respons emosional Anda.",
                "Batasi kafein dan gula karena dapat memperburuk gejala fisik ansietas.",
                "Olahraga aerobik ringan (jalan kaki, berenang) minimal 30 menit/hari.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Untuk terapi Cognitive Behavioral Therapy (CBT) yang terbukti efektif menangani ansietas."},
                {"siapa": "Psikiater", "alasan": "Jika gejala berat atau sudah berlangsung >6 bulan, evaluasi medikasi mungkin diperlukan."},
                {"siapa": "Hotline Into The Light Indonesia", "alasan": "Nomor: 119 ext 8 — tersedia 24 jam untuk dukungan krisis."},
            ],
            "urgensi": "medium"
        }
    },
    "P02": {
        "nama_penyakit": "KETIDAKBERDAYAAN",
        "kategori": "mood",
        "deskripsi": (
            "Ketidakberdayaan adalah kondisi di mana seseorang merasa tidak mampu "
            "mengendalikan situasi kehidupannya, kehilangan rasa otonom, dan merasa bahwa "
            "usaha apapun tidak akan mengubah keadaan. Kondisi ini sering muncul setelah "
            "trauma, penyakit kronis, atau tekanan hidup berkepanjangan. "
            "Tanpa penanganan, ketidakberdayaan dapat berkembang menjadi depresi klinis."
        ),
        "gejala": {
            "G12": {"nama": "Merasa tidak mampu mengendalikan situasi",               "cf_pakar": 0.92},
            "G13": {"nama": "Merasa tidak dapat menghasilkan sesuatu",                "cf_pakar": 0.99},
            "G14": {"nama": "Frustrasi terhadap ketidakmampuan beraktivitas",         "cf_pakar": 0.98},
            "G15": {"nama": "Ragu-ragu terhadap peran diri sendiri",                  "cf_pakar": 0.96},
            "G16": {"nama": "Mengungkapkan ketidakmampuan merawat diri",              "cf_pakar": 0.93},
            "G17": {"nama": "Tidak mampu mencari informasi perawatan diri",           "cf_pakar": 0.91},
            "G18": {"nama": "Tidak berpartisipasi dalam pengambilan keputusan",       "cf_pakar": 0.93},
            "G19": {"nama": "Enggan mengungkapkan perasaan sebenarnya",               "cf_pakar": 0.99},
            "G20": {"nama": "Ketergantungan pada orang lain disertai iritabilitas",   "cf_pakar": 0.98},
            "G21": {"nama": "Gagal mempertahankan pendapat saat mendapat perlawanan", "cf_pakar": 0.98},
        },
        "rekomendasi": {
            "ringkas": "Membangun harapan positif dan rasa kontrol diri",
            "detail": [
                "Buat daftar hal-hal kecil yang masih bisa Anda kendalikan setiap hari.",
                "Tetapkan satu tujuan kecil yang dapat dicapai per hari untuk membangun rasa percaya diri.",
                "Afirmasi positif harian: tulis 3 kalimat positif tentang kemampuan Anda.",
                "Bergabung dengan kelompok dukungan sebaya (peer support group).",
                "Hindari isolasi sosial — ceritakan perasaan pada orang yang dipercaya.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Terapi individu untuk mengidentifikasi pola pikir negatif dan membangun kembali rasa efikasi diri."},
                {"siapa": "Konselor atau Psikoterapis", "alasan": "Pendampingan terstruktur dalam membangun strategi koping positif."},
                {"siapa": "Yayasan Pulih", "alasan": "Telp: (021) 788-42580 — layanan konsultasi psikologis terjangkau."},
            ],
            "urgensi": "medium"
        }
    },
    "P03": {
        "nama_penyakit": "GANGGUAN CITRA TUBUH",
        "kategori": "persepsi_diri",
        "deskripsi": (
            "Gangguan citra tubuh terjadi ketika seseorang memiliki persepsi yang sangat negatif, "
            "terdistorsi, atau tidak akurat tentang tubuhnya sendiri. Kondisi ini dapat dipicu "
            "oleh perubahan fisik akibat penyakit, kecelakaan, operasi, atau tekanan sosial-budaya "
            "tentang standar kecantikan. Penderita seringkali merasa malu, menghindari cermin atau "
            "situasi sosial, dan menghabiskan banyak waktu memikirkan kekurangan fisiknya."
        ),
        "gejala": {
            "G22": {"nama": "Hilangnya bagian tubuh (akibat amputasi/operasi)",          "cf_pakar": 1.00},
            "G23": {"nama": "Perubahan bentuk atau fungsi anggota tubuh",                "cf_pakar": 1.00},
            "G24": {"nama": "Menyembunyikan atau memamerkan bagian tubuh bermasalah",    "cf_pakar": 0.96},
            "G25": {"nama": "Menolak melihat bagian tubuh tertentu",                     "cf_pakar": 0.99},
            "G26": {"nama": "Menolak menyentuh bagian tubuh tertentu",                   "cf_pakar": 0.98},
            "G27": {"nama": "Aktivitas sosial menurun drastis",                          "cf_pakar": 0.95},
            "G28": {"nama": "Mengungkapkan rasa malu atau bersalah tentang tubuh",       "cf_pakar": 0.98},
            "G30": {"nama": "Sering mengucapkan hal negatif tentang diri sendiri",       "cf_pakar": 1.00},
            "G31": {"nama": "Kesulitan membuat keputusan sehari-hari",                   "cf_pakar": 0.98},
        },
        "rekomendasi": {
            "ringkas": "Dukungan psikososial dan komunikasi terapeutik",
            "detail": [
                "Latihan 'body scan meditation' untuk mengenal tubuh tanpa penilaian.",
                "Catat pikiran negatif tentang tubuh lalu tantang kebenarannya secara logis.",
                "Fokus pada fungsi tubuh (apa yang bisa dilakukan) bukan penampilan.",
                "Kurangi paparan media sosial yang memicu perbandingan fisik.",
                "Bergabung dengan komunitas positif yang merayakan keberagaman fisik.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Terapi CBT atau ACT (Acceptance and Commitment Therapy) sangat efektif untuk gangguan citra tubuh."},
                {"siapa": "Dokter Spesialis Jiwa (Psikiater)", "alasan": "Evaluasi apakah ada kondisi komorbid seperti BDD (Body Dysmorphic Disorder) yang memerlukan penanganan khusus."},
                {"siapa": "Support Group Into The Light", "alasan": "Komunitas dukungan mental — intothelightid.org"},
            ],
            "urgensi": "medium"
        }
    },
    "P04": {
        "nama_penyakit": "HARGA DIRI RENDAH SITUASIONAL",
        "kategori": "persepsi_diri",
        "deskripsi": (
            "Harga diri rendah situasional adalah penilaian diri yang negatif yang muncul "
            "sebagai respons terhadap situasi tertentu — misalnya kehilangan pekerjaan, kegagalan, "
            "atau penolakan. Berbeda dengan harga diri rendah kronis, kondisi ini bersifat "
            "sementara dan biasanya dapat pulih ketika situasi membaik. "
            "Tandanya adalah pola menyalahkan diri secara episodik pada individu yang sebelumnya "
            "memiliki evaluasi diri yang positif."
        ),
        "gejala": {
            "G32": {"nama": "Menjelek-jelekkan atau meremehkan diri sendiri",                        "cf_pakar": 0.98},
            "G33": {"nama": "Mengucapkan hal-hal negatif tentang diri",                              "cf_pakar": 0.90},
            "G34": {"nama": "Menyalahkan diri atas masalah (sebelumnya evaluasi diri positif)",     "cf_pakar": 1.00},
            "G35": {"nama": "Kesulitan membuat keputusan",                                           "cf_pakar": 0.98},
        },
        "rekomendasi": {
            "ringkas": "Membangun kembali harga diri melalui aktivitas positif",
            "detail": [
                "Identifikasi kekuatan dan pencapaian yang pernah diraih, tulis dalam jurnal.",
                "Tetapkan tujuan realistis dan rayakan setiap pencapaian kecil.",
                "Praktikkan self-compassion: perlakukan diri sendiri dengan kebaikan yang sama seperti pada teman.",
                "Cari aktivitas yang memberikan rasa kompeten dan keberhasilan.",
                "Batasi waktu dengan orang atau lingkungan yang cenderung merendahkan.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Pendampingan dalam mengenali pola pikir self-defeating dan membangun strategi koping."},
                {"siapa": "Konselor Kampus/Kerja", "alasan": "Sumber daya yang mudah diakses untuk dukungan situasional."},
                {"siapa": "Sejiwa Foundation", "alasan": "Hotline: 119 ext 8 — dukungan kesehatan jiwa nasional."},
            ],
            "urgensi": "low"
        }
    },
    "P05": {
        "nama_penyakit": "KEPUTUSASAAN",
        "kategori": "mood",
        "deskripsi": (
            "Keputusasaan adalah kondisi emosional di mana seseorang kehilangan harapan bahwa "
            "masa depan akan membaik atau usahanya akan membuahkan hasil. "
            "Kondisi ini seringkali mendahului atau menyertai depresi berat, dan merupakan "
            "faktor risiko penting untuk perilaku bunuh diri. Tanda utamanya adalah pandangan "
            "negatif yang menetap terhadap masa depan, diri sendiri, dan lingkungan (cognitive triad Beck)."
        ),
        "gejala": {
            "G36": {"nama": "Mengungkapkan hidup terasa tanpa harapan atau hampa",  "cf_pakar": 0.95},
            "G37": {"nama": "Sering mengeluh dan tampak murung",                    "cf_pakar": 0.88},
            "G38": {"nama": "Kurang atau tidak mau berbicara sama sekali",          "cf_pakar": 0.90},
            "G39": {"nama": "Ekspresi wajah datar atau tumpul (afek datar)",        "cf_pakar": 0.92},
            "G40": {"nama": "Menarik diri dari lingkungan sosial",                  "cf_pakar": 0.89},
            "G41": {"nama": "Tidak ada selera makan atau makan berlebihan",         "cf_pakar": 0.87},
            "G42": {"nama": "Bersikap pasif, tidak bersemangat dalam aktivitas",   "cf_pakar": 0.86},
        },
        "rekomendasi": {
            "ringkas": "Latihan berpikir positif dan penemuan makna hidup",
            "detail": [
                "Terapi hope-based: identifikasi satu hal kecil yang masih diinginkan di masa depan.",
                "Latihan rasa syukur harian: tulis 3 hal positif yang terjadi hari ini.",
                "Libatkan diri dalam kegiatan bermakna: voluntarisme, seni, olahraga.",
                "Hindari konsumsi alkohol atau zat yang memperburuk mood.",
                "Bangun rutinitas harian yang teratur — tidur, makan, aktivitas fisik.",
            ],
            "hubungi": [
                {"siapa": "Psikiater", "alasan": "Evaluasi apakah ada gangguan depresi mayor yang memerlukan medikasi antidepresan."},
                {"siapa": "Psikolog Klinis", "alasan": "Terapi berbasis makna (Logotherapy) atau CBT untuk merekonstruksi pola pikir hopeless."},
                {"siapa": "Hotline Sejiwa", "alasan": "Nomor: 119 ext 8 — gratis, 24 jam, seluruh Indonesia."},
            ],
            "urgensi": "high"
        }
    },
    "P06": {
        "nama_penyakit": "HALUSINASI",
        "kategori": "psikosis",
        "deskripsi": (
            "Halusinasi adalah persepsi sensorik yang terjadi tanpa adanya stimulus eksternal nyata. "
            "Penderita dapat mendengar suara, melihat bayangan, merasakan sentuhan, atau mencium "
            "bau yang tidak ada. Halusinasi merupakan gejala khas pada gangguan psikotik "
            "seperti skizofrenia, namun juga dapat muncul akibat demam tinggi, penggunaan obat-obatan, "
            "atau kondisi neurologis tertentu. Kondisi ini memerlukan evaluasi medis segera."
        ),
        "gejala": {
            "G43": {"nama": "Mendengar suara bisikan tanpa sumber nyata",       "cf_pakar": 0.98},
            "G44": {"nama": "Melihat bayangan atau objek yang tidak ada",       "cf_pakar": 0.95},
            "G45": {"nama": "Berbicara sendiri tanpa lawan bicara nyata",       "cf_pakar": 0.96},
            "G46": {"nama": "Mondar-mandir atau gelisah tanpa tujuan jelas",   "cf_pakar": 0.90},
            "G47": {"nama": "Menatap satu arah tanpa alasan",                   "cf_pakar": 0.93},
            "G48": {"nama": "Konsentrasi buruk, mudah teralihkan",             "cf_pakar": 0.88},
        },
        "rekomendasi": {
            "ringkas": "Latihan menghardik, aktivitas terjadwal, patuh obat",
            "detail": [
                "Teknik menghardik: saat suara muncul, katakan tegas 'Pergi! Kamu tidak nyata!' sambil menutup telinga.",
                "Alihkan perhatian ke aktivitas fisik atau sosial segera saat halusinasi muncul.",
                "Buat jadwal harian yang terstruktur untuk meminimalkan waktu 'kosong' yang memperparah halusinasi.",
                "Catat waktu dan pemicu halusinasi dalam buku harian untuk dibawa ke dokter.",
                "Pastikan kepatuhan minum obat antipsikotik sesuai resep dokter.",
            ],
            "hubungi": [
                {"siapa": "Psikiater (SEGERA)", "alasan": "Halusinasi adalah gejala psikotik yang WAJIB dievaluasi oleh dokter spesialis jiwa sesegera mungkin."},
                {"siapa": "IGD RS Jiwa terdekat", "alasan": "Jika halusinasi menyebabkan perilaku berbahaya — bawa segera ke IGD."},
                {"siapa": "RSJ Provinsi terdekat", "alasan": "Di Jawa Barat: RSJ Provinsi Jawa Barat, Jl. Kolonel Masturi No.7, Cimahi — Telp: (022) 6650871."},
            ],
            "urgensi": "high"
        }
    },
    "P07": {
        "nama_penyakit": "WAHAM",
        "kategori": "psikosis",
        "deskripsi": (
            "Waham adalah keyakinan yang kuat, salah, dan tidak dapat diubah meskipun sudah "
            "diberikan bukti yang bertentangan. Contohnya: waham kebesaran (merasa sebagai tokoh "
            "penting/penyelamat dunia), waham curiga (merasa selalu diawasi atau dianiaya), "
            "atau waham referensi (merasa pesan di TV/radio ditujukan khusus untuknya). "
            "Waham adalah gejala utama psikosis dan memerlukan penanganan medis segera."
        ),
        "gejala": {
            "G49": {"nama": "Keyakinan tidak sesuai realita (kebesaran/curiga)",        "cf_pakar": 0.97},
            "G50": {"nama": "Curiga berlebihan terhadap orang di sekitar",              "cf_pakar": 0.94},
            "G51": {"nama": "Bicara berlebihan atau melompat-lompat topik",             "cf_pakar": 0.88},
            "G52": {"nama": "Wajah tegang, ekspresi tidak sesuai konteks",             "cf_pakar": 0.86},
        },
        "rekomendasi": {
            "ringkas": "Orientasi realita, latihan kemampuan positif, patuh obat",
            "detail": [
                "Jangan memperdebatkan atau memvalidasi keyakinan waham — fokus pada realita secara halus.",
                "Latihan orientasi realita: bantu penderita mengenali tempat, waktu, dan identitas secara rutin.",
                "Ciptakan lingkungan yang aman dan dapat diprediksi untuk mengurangi kecurigaan.",
                "Dukung kepatuhan minum obat antipsikotik — ini adalah intervensi utama.",
                "Keluarga perlu mendapatkan edukasi tentang cara berkomunikasi dengan penderita waham.",
            ],
            "hubungi": [
                {"siapa": "Psikiater (SEGERA)", "alasan": "Waham adalah gejala psikotik akut yang memerlukan evaluasi dan penanganan obat segera."},
                {"siapa": "Tim Kesehatan Jiwa Puskesmas", "alasan": "Program ODGJ di Puskesmas dapat membantu rujukan dan monitoring rutin."},
                {"siapa": "RSJ Provinsi Jawa Barat", "alasan": "Telp: (022) 6650871 — tersedia layanan rawat jalan dan rawat inap psikiatri."},
            ],
            "urgensi": "high"
        }
    },
    "P08": {
        "nama_penyakit": "PERILAKU KEKERASAN",
        "kategori": "perilaku",
        "deskripsi": (
            "Perilaku kekerasan dalam konteks psikiatri merujuk pada tindakan agresif verbal "
            "maupun fisik yang ditujukan kepada diri sendiri, orang lain, atau benda di sekitar. "
            "Kondisi ini dapat menjadi gejala dari berbagai gangguan jiwa seperti psikosis, "
            "gangguan bipolar fase manik, atau gangguan kepribadian. "
            "Bila tidak ditangani, perilaku ini dapat membahayakan keselamatan penderita dan orang lain."
        ),
        "gejala": {
            "G53": {"nama": "Mengancam atau mengumpat dengan kata-kata kasar",        "cf_pakar": 0.96},
            "G54": {"nama": "Menyerang orang lain atau merusak barang",              "cf_pakar": 0.99},
            "G55": {"nama": "Mata melotot, tangan mengepal, wajah memerah",          "cf_pakar": 0.95},
            "G56": {"nama": "Postur tubuh kaku dan sangat tegang",                   "cf_pakar": 0.90},
        },
        "rekomendasi": {
            "ringkas": "Latihan manajemen marah, de-eskalasi, dan patuh obat",
            "detail": [
                "Teknik de-eskalasi: beri ruang fisik, bicara pelan dan tenang, hindari kontak mata langsung yang intens.",
                "Latihan manajemen marah: identifikasi pemicu, gunakan teknik time-out sebelum bereaksi.",
                "Olahraga fisik sebagai saluran energi agresi: lari, boxing dengan sansak.",
                "Teknik relaksasi progresif untuk mengurangi ketegangan otot saat marah.",
                "Kepatuhan minum obat penstabil mood atau antipsikotik sangat penting.",
            ],
            "hubungi": [
                {"siapa": "Psikiater (SEGERA)", "alasan": "Evaluasi medis segera diperlukan untuk menentukan penyebab dan terapi yang tepat."},
                {"siapa": "IGD RS atau Polisi", "alasan": "Jika ada ancaman kekerasan fisik yang nyata — hubungi 110 atau bawa ke IGD terdekat."},
                {"siapa": "RSJ Provinsi Jawa Barat", "alasan": "Telp: (022) 6650871 — tersedia layanan gawat darurat psikiatri."},
            ],
            "urgensi": "high"
        }
    },
    "P09": {
        "nama_penyakit": "HARGA DIRI RENDAH KRONIS",
        "kategori": "persepsi_diri",
        "deskripsi": (
            "Harga diri rendah kronis adalah evaluasi diri yang negatif, menetap, dan berlangsung "
            "dalam jangka panjang — bukan sebagai respons terhadap situasi tertentu. "
            "Kondisi ini berakar pada pengalaman masa kecil seperti pengabaian, kekerasan, "
            "atau kritik berulang. Penderita secara konsisten menilai dirinya tidak berharga, "
            "tidak kompeten, atau tidak layak dicintai, yang berdampak luas pada hubungan "
            "sosial, karier, dan kesehatan mental secara keseluruhan."
        ),
        "gejala": {
            "G57": {"nama": "Berjalan menunduk, postur tubuh lemah",                       "cf_pakar": 0.88},
            "G58": {"nama": "Kontak mata minimal atau menghindari kontak mata",            "cf_pakar": 0.91},
            "G59": {"nama": "Berbicara pelan, lirih, dan tidak tegas",                    "cf_pakar": 0.89},
            "G60": {"nama": "Bergantung penuh pada keputusan orang lain",                  "cf_pakar": 0.90},
            "G61": {"nama": "Menilai diri negatif atau merasa tidak berguna secara kronis","cf_pakar": 0.95},
        },
        "rekomendasi": {
            "ringkas": "Identifikasi kemampuan positif dan latihan kegiatan sesuai kemampuan",
            "detail": [
                "Terapi Schema: identifikasi 'skema maladaptif awal' yang berakar dari masa kecil.",
                "Buat 'prestasi jurnal': rekam setiap hal yang berhasil dilakukan, sekecil apapun.",
                "Latihan assertiveness: belajar mengungkapkan pendapat dan kebutuhan secara tegas namun sopan.",
                "Batas penggunaan media sosial yang memicu perbandingan negatif.",
                "Kembangkan satu keahlian atau hobi yang memberikan rasa kompeten dan pencapaian.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Schema Therapy atau Compassion-Focused Therapy (CFT) sangat efektif untuk harga diri rendah kronis."},
                {"siapa": "Konselor dengan spesialisasi inner child", "alasan": "Pendampingan untuk memproses luka masa kecil yang menjadi akar masalah."},
                {"siapa": "Yayasan Pulih", "alasan": "Telp: (021) 788-42580 — konsultasi psikologis dengan biaya terjangkau."},
            ],
            "urgensi": "medium"
        }
    },
    "P10": {
        "nama_penyakit": "ISOLASI SOSIAL",
        "kategori": "sosial",
        "deskripsi": (
            "Isolasi sosial adalah kondisi di mana seseorang secara aktif menghindari interaksi "
            "sosial atau mengalami keterputusan yang tidak diinginkan dari jaringan sosialnya. "
            "Ini berbeda dari introversi (yang merupakan preferensi normal). "
            "Isolasi sosial dapat memperburuk hampir semua gangguan kesehatan mental dan "
            "dikaitkan dengan peningkatan risiko depresi, kecemasan, bahkan masalah fisik "
            "seperti penyakit jantung dan penurunan fungsi imun."
        ),
        "gejala": {
            "G62": {"nama": "Menyatakan ingin sendirian, tidak mau bergaul",       "cf_pakar": 0.93},
            "G63": {"nama": "Menolak berinteraksi dengan orang lain",              "cf_pakar": 0.95},
            "G64": {"nama": "Tidak ada kontak mata saat berinteraksi",             "cf_pakar": 0.88},
            "G65": {"nama": "Malas atau tidak mau beraktivitas bersama orang lain","cf_pakar": 0.90},
        },
        "rekomendasi": {
            "ringkas": "Latihan berkenalan bertahap dari 1 orang lalu kelompok",
            "detail": [
                "Mulai dari interaksi kecil dan aman: sapa tetangga, bicara dengan kasir.",
                "Bergabung dengan komunitas berbasis minat (klub buku, olahraga, seni) untuk mengurangi tekanan sosial.",
                "Buat 'jadwal sosial': rencanakan satu interaksi sosial per minggu, tingkatkan perlahan.",
                "Latihan keterampilan sosial (social skills training) bersama terapis.",
                "Manfaatkan teknologi secara sehat: video call dengan teman/keluarga.",
            ],
            "hubungi": [
                {"siapa": "Psikolog Klinis", "alasan": "Social Skills Training (SST) dan terapi kelompok sangat efektif untuk isolasi sosial."},
                {"siapa": "Konselor atau Terapis", "alasan": "Pendampingan dalam mengidentifikasi penyebab dan membangun kepercayaan dalam berinteraksi."},
                {"siapa": "Komunitas Kesehatan Mental Indonesia (KPSI)", "alasan": "Grup dukungan sebaya yang aman — kpsi.or.id"},
            ],
            "urgensi": "medium"
        }
    },
    "P11": {
        "nama_penyakit": "DEFISIT PERAWATAN DIRI",
        "kategori": "perilaku",
        "deskripsi": (
            "Defisit perawatan diri adalah kondisi di mana seseorang tidak mampu atau tidak mau "
            "melakukan aktivitas perawatan dasar seperti mandi, berpakaian, makan, dan toileting "
            "secara mandiri. Kondisi ini sering merupakan manifestasi dari gangguan jiwa berat "
            "seperti depresi berat, skizofrenia, atau disabilitas kognitif. "
            "Selain berdampak pada kesehatan fisik, kondisi ini juga mempengaruhi harga diri "
            "dan interaksi sosial penderita."
        ),
        "gejala": {
            "G66": {"nama": "Mengatakan malas mandi atau tidak mampu merawat diri",  "cf_pakar": 0.93},
            "G67": {"nama": "Rambut kotor, gigi kotor, kulit berdaki",              "cf_pakar": 0.97},
            "G68": {"nama": "Kuku panjang dan kotor",                               "cf_pakar": 0.92},
            "G69": {"nama": "Pakaian kotor, tidak rapi, atau tidak sesuai",          "cf_pakar": 0.90},
            "G70": {"nama": "Makan berceceran atau tidak mampu makan sendiri",      "cf_pakar": 0.88},
        },
        "rekomendasi": {
            "ringkas": "Latihan kebersihan diri, makan, dan kemandirian sehari-hari",
            "detail": [
                "Buat jadwal harian perawatan diri yang sederhana dan tempel di tempat yang mudah terlihat.",
                "Mulai dengan satu kebiasaan perawatan diri per minggu, tambahkan secara bertahap.",
                "Gunakan sistem reward sederhana setiap berhasil melakukan perawatan diri.",
                "Minta bantuan keluarga untuk mendampingi tanpa mengambil alih sepenuhnya.",
                "Identifikasi hambatan spesifik (tidak ada energi, tidak termotivasi) dan atasi satu per satu.",
            ],
            "hubungi": [
                {"siapa": "Psikiater", "alasan": "Defisit perawatan diri sering merupakan gejala gangguan jiwa yang memerlukan pengobatan medis."},
                {"siapa": "Perawat Jiwa / Okupasi Terapis", "alasan": "Bantuan praktis dalam melatih kemandirian aktivitas sehari-hari (ADL training)."},
                {"siapa": "Puskesmas CMHN (Community Mental Health Nursing)", "alasan": "Program kunjungan rumah untuk pasien jiwa — hubungi Puskesmas terdekat."},
            ],
            "urgensi": "medium"
        }
    },
    "P12": {
        "nama_penyakit": "RISIKO BUNUH DIRI",
        "kategori": "kritis",
        "deskripsi": (
            "Risiko bunuh diri adalah kondisi di mana seseorang memiliki pemikiran, niat, "
            "atau rencana untuk mengakhiri hidupnya. Ini merupakan kondisi darurat kesehatan "
            "jiwa yang memerlukan penanganan segera. Faktor risiko meliputi depresi berat, "
            "riwayat percobaan bunuh diri, isolasi sosial, penggunaan zat, dan akses ke alat "
            "berbahaya. Perhatian dan intervensi dini dari lingkungan terdekat sangat menentukan."
        ),
        "gejala": {
            "G71": {"nama": "Mengungkapkan keinginan untuk mengakhiri hidup",                  "cf_pakar": 1.00},
            "G72": {"nama": "Mencari atau mengumpulkan benda-benda berbahaya",                 "cf_pakar": 0.99},
            "G73": {"nama": "Membuat surat wasiat atau berpamitan kepada orang-orang",         "cf_pakar": 0.98},
            "G74": {"nama": "Euforia mendadak setelah periode depresi berat",                  "cf_pakar": 0.95},
            "G75": {"nama": "Merasa tidak berharga atau menjadi beban bagi orang lain",        "cf_pakar": 0.93},
        },
        "rekomendasi": {
            "ringkas": "DARURAT — Hubungi bantuan profesional SEGERA",
            "detail": [
                "JANGAN tinggalkan orang tersebut sendirian — dampingi terus.",
                "Singkirkan akses ke benda-benda berbahaya (obat-obatan, senjata, dll).",
                "Dengarkan tanpa menghakimi — validasi perasaan, bukan tindakannya.",
                "Jangan buat janji untuk merahasiakan keinginan bunuh diri.",
                "Buat 'safety plan': siapa yang dihubungi, ke mana pergi, apa yang dilakukan saat krisis.",
            ],
            "hubungi": [
                {"siapa": "119 ext 8 (Hotline Jiwa Nasional)", "alasan": "GRATIS, 24 jam — hubungi SEKARANG jika ada risiko langsung."},
                {"siapa": "IGD Rumah Sakit Terdekat", "alasan": "Bawa segera ke IGD jika ada percobaan atau ancaman langsung — ini adalah kondisi DARURAT MEDIS."},
                {"siapa": "Into The Light Indonesia", "alasan": "WhatsApp: 081284264796 — layanan dukungan krisis dan pencegahan bunuh diri."},
            ],
            "urgensi": "critical"
        }
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# DEFINISI KATEGORI
# ──────────────────────────────────────────────────────────────────────────────

KATEGORI = {
    "mood": {
        "label": "Gangguan Suasana Hati & Emosi",
        "icon": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z",
        "deskripsi": "Mencakup kondisi seperti kecemasan berlebihan, keputusasaan, dan ketidakberdayaan.",
        "warna": "amber"
    },
    "persepsi_diri": {
        "label": "Gangguan Persepsi & Harga Diri",
        "icon": "M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z",
        "deskripsi": "Mencakup masalah citra tubuh, harga diri rendah, dan persepsi negatif terhadap diri sendiri.",
        "warna": "rose"
    },
    "psikosis": {
        "label": "Gejala Psikotik",
        "icon": "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
        "deskripsi": "Mencakup halusinasi, waham, dan gangguan persepsi realita. Memerlukan penanganan segera.",
        "warna": "purple"
    },
    "sosial": {
        "label": "Gangguan Fungsi Sosial",
        "icon": "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
        "deskripsi": "Mencakup isolasi sosial dan kesulitan dalam membangun atau mempertahankan hubungan.",
        "warna": "blue"
    },
    "perilaku": {
        "label": "Gangguan Perilaku",
        "icon": "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
        "deskripsi": "Mencakup perilaku kekerasan dan defisit perawatan diri.",
        "warna": "orange"
    },
    "kritis": {
        "label": "Kondisi Darurat",
        "icon": "M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01",
        "deskripsi": "Kondisi yang memerlukan penanganan darurat segera dari profesional medis.",
        "warna": "red"
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# HELPER: CF CALCULATION
# ──────────────────────────────────────────────────────────────────────────────

def hitung_cf_kombinasi(cf_list):
    if not cf_list:
        return 0.0
    cf_lama = cf_list[0]
    for i in range(1, len(cf_list)):
        cf_baru = cf_list[i]
        cf_lama = cf_lama + cf_baru * (1 - cf_lama)
    return cf_lama


def jalankan_diagnosa(user_inputs, kode_penyakit_list=None):
    """Jalankan inference engine untuk daftar kode penyakit tertentu atau semua."""
    targets = kode_penyakit_list or list(KNOWLEDGE_BASE.keys())
    hasil = []
    for p_kode in targets:
        if p_kode not in KNOWLEDGE_BASE:
            continue
        p_data = KNOWLEDGE_BASE[p_kode]
        cf_terkumpul = []
        gejala_cocok = []
        for g_kode, g_data in p_data["gejala"].items():
            cf_user = float(user_inputs.get(g_kode, 0.0))
            if cf_user > 0.0:
                cf_gabungan = g_data["cf_pakar"] * cf_user
                cf_terkumpul.append(cf_gabungan)
                gejala_cocok.append(g_kode)
        if cf_terkumpul:
            total_g = len(p_data["gejala"])
            nilai_cf = hitung_cf_kombinasi(cf_terkumpul)
            rasio    = len(gejala_cocok) / total_g
            persen   = round(nilai_cf * rasio * 100, 2)
            if persen > 0:
                hasil.append({
                    "kode_penyakit":   p_kode,
                    "nama_penyakit":   p_data["nama_penyakit"],
                    "kategori":        p_data["kategori"],
                    "deskripsi":       p_data["deskripsi"],
                    "gejala_match":    len(gejala_cocok),
                    "total_gejala":    total_g,
                    "keyakinan":       persen,
                    "rekomendasi":     p_data["rekomendasi"],
                })
    hasil.sort(key=lambda x: x["keyakinan"], reverse=True)
    return hasil

# ──────────────────────────────────────────────────────────────────────────────
# ADMIN CREDENTIALS (ganti dengan hash di produksi)
# ──────────────────────────────────────────────────────────────────────────────
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ──────────────────────────────────────────────────────────────────────────────
# ROUTES — PUBLIC
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pilih_metode")
def pilih_metode():
    return render_template("pilih_metode.html")

@app.route("/asesmen_manual")
def asesmen_manual():
    kategori_list = []
    for k_id, k_data in KATEGORI.items():
        gejala_unik = set()
        penyakit_count = 0
        for p_data in KNOWLEDGE_BASE.values():
            if p_data["kategori"] == k_id:
                penyakit_count += 1
                for g_kode in p_data["gejala"]:
                    gejala_unik.add(g_kode)
        
        jumlah_pertanyaan = len(gejala_unik)
        waktu_menit = max(1, jumlah_pertanyaan // 4)
        waktu_str = f"{waktu_menit} - {waktu_menit + 2} menit"
        
        kategori_list.append({
            "id": k_id,
            "label": k_data["label"],
            "icon": k_data["icon"],
            "deskripsi": k_data["deskripsi"],
            "warna": k_data["warna"],
            "jumlah_pertanyaan": jumlah_pertanyaan,
            "perkiraan_waktu": waktu_str,
            "jumlah_penyakit": penyakit_count,
        })
    return render_template("asesmen_manual.html", kategori_list=kategori_list)


@app.route("/asesmen/<kategori_id>")
def asesmen(kategori_id):
    if kategori_id not in KATEGORI:
        return redirect(url_for("index"))
    # Kumpulkan semua gejala unik dalam kategori ini
    penyakit_dalam = {
        k: v for k, v in KNOWLEDGE_BASE.items() if v["kategori"] == kategori_id
    }
    gejala_list = {}
    for p_data in penyakit_dalam.values():
        for g_kode, g_data in p_data["gejala"].items():
            if g_kode not in gejala_list:
                gejala_list[g_kode] = g_data["nama"]
    gejala_sorted = [{"kode": k, "nama": v} for k, v in sorted(gejala_list.items())]
    penyakit_kode_list = list(penyakit_dalam.keys())
    kat_info = KATEGORI[kategori_id]
    penyakit_info = [
        {"kode": pk, "nama": pv["nama_penyakit"], "deskripsi": pv["deskripsi"]}
        for pk, pv in penyakit_dalam.items()
    ]
    return render_template(
        "asesmen.html",
        kategori_id=kategori_id,
        kategori_info=kat_info,
        gejala=gejala_sorted,
        penyakit_kode_list=json.dumps(penyakit_kode_list),
        penyakit_info=penyakit_info,
    )


@app.route("/diagnosa", methods=["POST"])
def diagnosa():
    data = request.json
    penyakit_kode_list = data.pop("__penyakit_kode_list", None)
    user_inputs = {k: float(v) for k, v in data.items()}
    if penyakit_kode_list:
        hasil = jalankan_diagnosa(user_inputs, penyakit_kode_list)
    else:
        hasil = jalankan_diagnosa(user_inputs)
    return jsonify(hasil)

# ──────────────────────────────────────────────────────────────────────────────
# ROUTES — ADMIN
# ──────────────────────────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and \
           request.form.get("password") == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Username atau password salah."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    summary = []
    for p_kode, p_data in KNOWLEDGE_BASE.items():
        summary.append({
            "kode": p_kode,
            "nama": p_data["nama_penyakit"],
            "kategori": KATEGORI.get(p_data["kategori"], {}).get("label", p_data["kategori"]),
            "jumlah_gejala": len(p_data["gejala"]),
            "urgensi": p_data["rekomendasi"]["urgensi"],
        })
    return render_template("admin_dashboard.html", penyakit_list=summary, kategori=KATEGORI)


@app.route("/admin/penyakit/<p_kode>")
@admin_required
def admin_detail_penyakit(p_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return redirect(url_for("admin_dashboard"))
    p_data = KNOWLEDGE_BASE[p_kode]
    return render_template(
        "admin_detail.html",
        p_kode=p_kode,
        p_data=p_data,
        kategori=KATEGORI
    )


# ── API Admin: Update nama/kategori/deskripsi penyakit
@app.route("/admin/api/penyakit/<p_kode>", methods=["PUT"])
@admin_required
def api_update_penyakit(p_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404
    body = request.json
    if "nama_penyakit" in body:
        KNOWLEDGE_BASE[p_kode]["nama_penyakit"] = body["nama_penyakit"].upper().strip()
    if "kategori" in body:
        KNOWLEDGE_BASE[p_kode]["kategori"] = body["kategori"]
    if "deskripsi" in body:
        KNOWLEDGE_BASE[p_kode]["deskripsi"] = body["deskripsi"]
    if "rekomendasi_ringkas" in body:
        KNOWLEDGE_BASE[p_kode]["rekomendasi"]["ringkas"] = body["rekomendasi_ringkas"]
    if "urgensi" in body:
        KNOWLEDGE_BASE[p_kode]["rekomendasi"]["urgensi"] = body["urgensi"]
    return jsonify({"status": "ok", "kode": p_kode})


# ── API Admin: Update CF pakar suatu gejala
@app.route("/admin/api/penyakit/<p_kode>/gejala/<g_kode>", methods=["PUT"])
@admin_required
def api_update_gejala(p_kode, g_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404
    if g_kode not in KNOWLEDGE_BASE[p_kode]["gejala"]:
        return jsonify({"error": "Gejala tidak ditemukan"}), 404
    body = request.json
    if "nama" in body:
        KNOWLEDGE_BASE[p_kode]["gejala"][g_kode]["nama"] = body["nama"]
    if "cf_pakar" in body:
        val = float(body["cf_pakar"])
        if not (0.0 <= val <= 1.0):
            return jsonify({"error": "CF harus antara 0.0 dan 1.0"}), 400
        KNOWLEDGE_BASE[p_kode]["gejala"][g_kode]["cf_pakar"] = round(val, 2)
    return jsonify({"status": "ok", "gejala": KNOWLEDGE_BASE[p_kode]["gejala"][g_kode]})


# ── API Admin: Tambah gejala baru ke penyakit
@app.route("/admin/api/penyakit/<p_kode>/gejala", methods=["POST"])
@admin_required
def api_tambah_gejala(p_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404
    body = request.json
    nama  = body.get("nama", "").strip()
    cf    = float(body.get("cf_pakar", 0.8))
    g_kode = body.get("kode", "").strip().upper()
    if not nama or not g_kode:
        return jsonify({"error": "Kode dan nama gejala wajib diisi"}), 400
    if not (0.0 <= cf <= 1.0):
        return jsonify({"error": "CF harus antara 0.0 dan 1.0"}), 400
    KNOWLEDGE_BASE[p_kode]["gejala"][g_kode] = {"nama": nama, "cf_pakar": round(cf, 2)}
    return jsonify({"status": "ok", "kode": g_kode})


# ── API Admin: Hapus gejala dari penyakit
@app.route("/admin/api/penyakit/<p_kode>/gejala/<g_kode>", methods=["DELETE"])
@admin_required
def api_hapus_gejala(p_kode, g_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404
    if g_kode not in KNOWLEDGE_BASE[p_kode]["gejala"]:
        return jsonify({"error": "Gejala tidak ditemukan"}), 404
    if len(KNOWLEDGE_BASE[p_kode]["gejala"]) <= 1:
        return jsonify({"error": "Minimal satu gejala harus ada"}), 400
    del KNOWLEDGE_BASE[p_kode]["gejala"][g_kode]
    return jsonify({"status": "ok"})


# ── API Admin: Tambah penyakit baru
@app.route("/admin/api/penyakit", methods=["POST"])
@admin_required
def api_tambah_penyakit():
    body = request.json
    kode = body.get("kode", "").strip().upper()
    nama = body.get("nama", "").strip().upper()
    kat  = body.get("kategori", "mood")
    if not kode or not nama:
        return jsonify({"error": "Kode dan nama penyakit wajib diisi"}), 400
    if kode in KNOWLEDGE_BASE:
        return jsonify({"error": f"Kode {kode} sudah digunakan"}), 400
    KNOWLEDGE_BASE[kode] = {
        "nama_penyakit": nama,
        "kategori": kat,
        "deskripsi": body.get("deskripsi", ""),
        "gejala": {},
        "rekomendasi": {
            "ringkas": body.get("rekomendasi_ringkas", ""),
            "detail": [],
            "hubungi": [],
            "urgensi": body.get("urgensi", "medium"),
        }
    }
    return jsonify({"status": "ok", "kode": kode})


# ── API Admin: Hapus penyakit
@app.route("/admin/api/penyakit/<p_kode>", methods=["DELETE"])
@admin_required
def api_hapus_penyakit(p_kode):
    if p_kode not in KNOWLEDGE_BASE:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404
    del KNOWLEDGE_BASE[p_kode]
    return jsonify({"status": "ok"})


# ── API Admin: Get semua data (untuk export/review)
@app.route("/admin/api/export")
@admin_required
def api_export():
    return jsonify(KNOWLEDGE_BASE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)