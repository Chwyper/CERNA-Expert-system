# =====================================================================
# SISTEM PAKAR DIAGNOSA SPESIALIS JIWA
# Metode: Forward Chaining + Depth-First Search (DFS) + Certainty Factor
# Knowledge Base: SAK Psikososial UI 2012 + SAK Jiwa RS Cimahi 2007
# Versi: 2.0 (P01-P12, G01-G75)
# =====================================================================

def hitung_cf_kombinasi(cf_list):
    """
    Menghitung nilai kombinasi Certainty Factor (CF) dari kumpulan gejala.
    Rumus: CF_Lama + CF_Baru * (1 - CF_Lama)
    """
    if not cf_list:
        return 0.0

    cf_lama = cf_list[0]
    for i in range(1, len(cf_list)):
        cf_baru = cf_list[i]
        cf_lama = cf_lama + cf_baru * (1 - cf_lama)

    return cf_lama


# ---------------------------------------------------------------------
# 1. KNOWLEDGE BASE (BASIS PENGETAHUAN)
#    Sumber: SAK Psikososial UI 2012 & SAK Jiwa RS Cimahi 2007
# ---------------------------------------------------------------------
knowledge_base = {

    # ── P01 ─────────────────────────────────────────────────────────
    "P01": {
        "nama_penyakit": "ANSIETAS",
        "gejala": {
            "G01": {"nama": "Sering napas pendek",                          "cf_pakar": 0.90},
            "G02": {"nama": "Nadi dan tekanan darah naik",                  "cf_pakar": 0.95},
            "G03": {"nama": "Mulut kering",                                 "cf_pakar": 0.90},
            "G04": {"nama": "Anoreksia",                                    "cf_pakar": 0.91},
            "G09": {"nama": "Sakit kepala",                                 "cf_pakar": 0.92},
            "G10": {"nama": "Sulit tidur",                                  "cf_pakar": 0.96},
            "G11": {"nama": "Berkeringat berlebih",                         "cf_pakar": 0.98},
        },
        "rekomendasi": "Teknik relaksasi (napas dalam, relaksasi otot progresif)"
    },

    # ── P02 ─────────────────────────────────────────────────────────
    "P02": {
        "nama_penyakit": "KETIDAKBERDAYAAN",
        "gejala": {
            "G12": {"nama": "Mengungkapkan tidak mampu mengendalikan atau mempengaruhi situasi",            "cf_pakar": 0.92},
            "G13": {"nama": "Mengungkapkan tidak dapat menghasilkan sesuatu",                              "cf_pakar": 0.99},
            "G14": {"nama": "Frustasi terhadap ketidakmampuan melakukan aktivitas sebelumnya",             "cf_pakar": 0.98},
            "G15": {"nama": "Keragu-raguan terhadap penampilan peran",                                     "cf_pakar": 0.96},
            "G16": {"nama": "Mengatakan ketidakmampuan perawatan diri",                                   "cf_pakar": 0.93},
            "G17": {"nama": "Tidak mampu mencari informasi tentang perawatan diri",                       "cf_pakar": 0.91},
            "G18": {"nama": "Tidak berpartisipasi dalam pengambilan keputusan",                            "cf_pakar": 0.93},
            "G19": {"nama": "Enggan mengungkapkan perasaan sebenarnya",                                    "cf_pakar": 0.99},
            "G20": {"nama": "Ketergantungan pada orang lain disertai iritabilitas, marah, atau rasa bersalah", "cf_pakar": 0.98},
            "G21": {"nama": "Gagal mempertahankan ide atau pendapat saat mendapat perlawanan",             "cf_pakar": 0.98},
        },
        "rekomendasi": "Mengembangkan harapan positif melalui afirmasi positif"
    },

    # ── P03 ─────────────────────────────────────────────────────────
    "P03": {
        "nama_penyakit": "GANGGUAN CITRA TUBUH",
        "gejala": {
            "G22": {"nama": "Hilangnya bagian tubuh",                                              "cf_pakar": 1.00},
            "G23": {"nama": "Perubahan anggota tubuh baik bentuk maupun fungsi",                   "cf_pakar": 1.00},
            "G24": {"nama": "Menyembunyikan atau memamerkan bagian tubuh yang terganggu",           "cf_pakar": 0.96},
            "G25": {"nama": "Menolak melihat bagian tubuh",                                        "cf_pakar": 0.99},
            "G26": {"nama": "Menolak menyentuh bagian tubuh",                                      "cf_pakar": 0.98},
            "G27": {"nama": "Aktivitas sosial menurun",                                            "cf_pakar": 0.95},
            "G28": {"nama": "Mengungkapkan rasa malu atau bersalah",                               "cf_pakar": 0.98},
            "G30": {"nama": "Mengungkapkan hal-hal negatif tentang diri sendiri",                  "cf_pakar": 1.00},
            "G31": {"nama": "Kesulitan dalam membuat keputusan",                                   "cf_pakar": 0.98},
        },
        "rekomendasi": "Dukungan psikososial melalui komunikasi terapeutik"
    },

    # ── P04 ─────────────────────────────────────────────────────────
    "P04": {
        "nama_penyakit": "HARGA DIRI RENDAH SITUASIONAL",
        "gejala": {
            "G32": {"nama": "Mengungkapkan atau menjelek-jelekkan diri",                                                          "cf_pakar": 0.98},
            "G33": {"nama": "Mengungkapkan hal-hal negatif tentang diri",                                                         "cf_pakar": 0.90},
            "G34": {"nama": "Menyalahkan diri secara episodik terhadap permasalahan hidup (sebelumnya evaluasi diri positif)",    "cf_pakar": 1.00},
            "G35": {"nama": "Kesulitan dalam membuat keputusan",                                                                  "cf_pakar": 0.98},
        },
        "rekomendasi": "Membangun kembali harga diri positif melalui kegiatan positif"
    },

    # ── P05 ─────────────────────────────────────────────────────────
    "P05": {
        "nama_penyakit": "KEPUTUSASAAN",
        "gejala": {
            "G36": {"nama": "Mengungkapkan situasi kehidupan terasa tanpa harapan atau hampa",  "cf_pakar": 0.95},
            "G37": {"nama": "Sering mengeluh dan nampak murung",                                "cf_pakar": 0.88},
            "G38": {"nama": "Kurang atau tidak mau berbicara sama sekali",                      "cf_pakar": 0.90},
            "G39": {"nama": "Afek datar atau tumpul",                                           "cf_pakar": 0.92},
            "G40": {"nama": "Menarik diri dari lingkungan",                                     "cf_pakar": 0.89},
            "G41": {"nama": "Menurun atau tidak adanya selera makan",                           "cf_pakar": 0.87},
            "G42": {"nama": "Bersikap pasif dalam menerima perawatan",                          "cf_pakar": 0.86},
        },
        "rekomendasi": "Latihan berpikir positif, penemuan harapan dan makna hidup"
    },

    # ── P06 ─────────────────────────────────────────────────────────
    "P06": {
        "nama_penyakit": "HALUSINASI",
        "gejala": {
            "G43": {"nama": "Mengatakan mendengar suara bisikan yang tidak ada sumbernya",  "cf_pakar": 0.98},
            "G44": {"nama": "Mengatakan melihat bayangan atau sesuatu yang tidak ada",     "cf_pakar": 0.95},
            "G45": {"nama": "Bicara sendiri tanpa lawan bicara yang nyata",                "cf_pakar": 0.96},
            "G46": {"nama": "Mondar-mandir atau gelisah tanpa tujuan jelas",               "cf_pakar": 0.90},
            "G47": {"nama": "Melihat atau menatap ke satu arah tanpa alasan",              "cf_pakar": 0.93},
            "G48": {"nama": "Konsentrasi buruk atau mudah teralihkan",                     "cf_pakar": 0.88},
        },
        "rekomendasi": "Latihan menghardik, bercakap-cakap, aktivitas terjadwal, patuh obat"
    },

    # ── P07 ─────────────────────────────────────────────────────────
    "P07": {
        "nama_penyakit": "WAHAM",
        "gejala": {
            "G49": {"nama": "Mengungkapkan keyakinan yang tidak sesuai realita (kebesaran, curiga, dll)", "cf_pakar": 0.97},
            "G50": {"nama": "Curiga berlebihan terhadap orang-orang di sekitarnya",                      "cf_pakar": 0.94},
            "G51": {"nama": "Bicara berlebihan atau melompat dari satu topik ke topik lain",             "cf_pakar": 0.88},
            "G52": {"nama": "Wajah tegang dan ekspresi tidak sesuai konteks",                            "cf_pakar": 0.86},
        },
        "rekomendasi": "Orientasi realita, latihan kemampuan positif, patuh obat"
    },

    # ── P08 ─────────────────────────────────────────────────────────
    "P08": {
        "nama_penyakit": "PERILAKU KEKERASAN",
        "gejala": {
            "G53": {"nama": "Mengancam atau mengumpat dengan kata-kata kasar",          "cf_pakar": 0.96},
            "G54": {"nama": "Menyerang orang lain atau merusak barang atau lingkungan", "cf_pakar": 0.99},
            "G55": {"nama": "Mata melotot, tangan mengepal, wajah memerah",             "cf_pakar": 0.95},
            "G56": {"nama": "Postur tubuh kaku dan tegang",                             "cf_pakar": 0.90},
        },
        "rekomendasi": "Latihan fisik, sosial atau verbal, spiritual, dan patuh obat"
    },

    # ── P09 ─────────────────────────────────────────────────────────
    "P09": {
        "nama_penyakit": "HARGA DIRI RENDAH KRONIS",
        "gejala": {
            "G57": {"nama": "Berjalan menunduk atau postur tubuh lemah",                "cf_pakar": 0.88},
            "G58": {"nama": "Kontak mata minimal atau menghindari kontak mata",         "cf_pakar": 0.91},
            "G59": {"nama": "Berbicara pelan, lirih, dan tidak tegas",                  "cf_pakar": 0.89},
            "G60": {"nama": "Bergantung penuh pada pendapat dan keputusan orang lain",  "cf_pakar": 0.90},
            "G61": {"nama": "Menilai diri negatif atau merasa tidak berguna secara kronis", "cf_pakar": 0.95},
        },
        "rekomendasi": "Identifikasi kemampuan positif, latihan kegiatan sesuai kemampuan"
    },

    # ── P10 ─────────────────────────────────────────────────────────
    "P10": {
        "nama_penyakit": "ISOLASI SOSIAL",
        "gejala": {
            "G62": {"nama": "Menyatakan ingin sendirian atau tidak mau bergaul",    "cf_pakar": 0.93},
            "G63": {"nama": "Menolak berinteraksi dengan orang lain",               "cf_pakar": 0.95},
            "G64": {"nama": "Tidak ada kontak mata saat berinteraksi",              "cf_pakar": 0.88},
            "G65": {"nama": "Malas atau tidak mau beraktivitas bersama orang lain", "cf_pakar": 0.90},
        },
        "rekomendasi": "Latihan berkenalan, berinteraksi bertahap dari 1 orang lalu kelompok"
    },

    # ── P11 ─────────────────────────────────────────────────────────
    "P11": {
        "nama_penyakit": "DEFISIT PERAWATAN DIRI",
        "gejala": {
            "G66": {"nama": "Mengatakan malas mandi atau tidak mampu merawat diri",   "cf_pakar": 0.93},
            "G67": {"nama": "Rambut kotor, gigi kotor, kulit berdaki",                "cf_pakar": 0.97},
            "G68": {"nama": "Kuku panjang dan kotor",                                 "cf_pakar": 0.92},
            "G69": {"nama": "Pakaian kotor, tidak rapi, atau tidak sesuai",           "cf_pakar": 0.90},
            "G70": {"nama": "Makan berceceran atau tidak mampu makan sendiri",        "cf_pakar": 0.88},
        },
        "rekomendasi": "Latihan kebersihan diri, berdandan, makan, serta BAB/BAK secara mandiri"
    },

    # ── P12 ─────────────────────────────────────────────────────────
    "P12": {
        "nama_penyakit": "RISIKO BUNUH DIRI",
        "gejala": {
            "G71": {"nama": "Mengungkapkan keinginan untuk mengakhiri hidup",                   "cf_pakar": 1.00},
            "G72": {"nama": "Mencari atau mengumpulkan benda-benda berbahaya",                  "cf_pakar": 0.99},
            "G73": {"nama": "Membuat surat wasiat atau berpamitan kepada orang-orang",          "cf_pakar": 0.98},
            "G74": {"nama": "Euforia mendadak setelah periode depresi berat",                   "cf_pakar": 0.95},
            "G75": {"nama": "Menyatakan merasa tidak berharga atau menjadi beban orang lain",   "cf_pakar": 0.93},
        },
        "rekomendasi": "Kontrak treatment, kendalikan dorongan, identifikasi aspek positif, koping konstruktif. SEGERA hubungi profesional medis."
    },
}


# ---------------------------------------------------------------------
# RIWAYAT USER (cache gejala agar tidak ditanya dua kali)
# ---------------------------------------------------------------------
gejala_dialami = {}

# Kumpulkan semua nama gejala untuk referensi
semua_gejala_nama = {}
for p_data in knowledge_base.values():
    for g_kode, g_data in p_data["gejala"].items():
        if g_kode not in semua_gejala_nama:
            semua_gejala_nama[g_kode] = g_data["nama"]


# ---------------------------------------------------------------------
# 2. MESIN INFERENSI — DFS REKURSIF
# ---------------------------------------------------------------------

def dfs_penelusuran_gejala(kode_penyakit, list_gejala, index, cf_terkumpul, gejala_cocok):
    """
    Fungsi rekursif untuk menelusuri gejala suatu penyakit secara DFS.
    Base case: index >= len(list_gejala) (semua daun sudah dikunjungi).
    """
    if index >= len(list_gejala):
        return cf_terkumpul, gejala_cocok

    g_kode = list_gejala[index]

    # Cek cache — tanya hanya jika belum pernah dijawab
    if g_kode not in gejala_dialami:
        print(f"\n[Evaluasi {knowledge_base[kode_penyakit]['nama_penyakit']}]")
        print(f"Apakah Anda mengalami [{g_kode}] {semua_gejala_nama[g_kode]}?")

        while True:
            jawaban = input("Pilih angka (1-5): ").strip()
            if jawaban == '1':   cf_user = 1.0; break
            elif jawaban == '2': cf_user = 0.8; break
            elif jawaban == '3': cf_user = 0.6; break
            elif jawaban == '4': cf_user = 0.4; break
            elif jawaban == '5': cf_user = 0.0; break
            else: print("Input tidak valid! Harap masukkan angka 1-5.")

        gejala_dialami[g_kode] = cf_user

    cf_user_val = gejala_dialami[g_kode]

    if cf_user_val > 0.0:
        cf_pakar = knowledge_base[kode_penyakit]["gejala"][g_kode]["cf_pakar"]
        cf_gejala_final = cf_pakar * cf_user_val
        cf_terkumpul.append(cf_gejala_final)
        gejala_cocok.append(g_kode)

    return dfs_penelusuran_gejala(kode_penyakit, list_gejala, index + 1, cf_terkumpul, gejala_cocok)


# ---------------------------------------------------------------------
# 3. SISTEM PAKAR UTAMA (CLI)
# ---------------------------------------------------------------------

def sistem_pakar():
    print("=" * 65)
    print("   SELAMAT DATANG DI SISTEM PAKAR DIAGNOSA SPESIALIS JIWA")
    print("   Versi 2.0 — 12 Diagnosa | 75 Gejala")
    print("=" * 65)
    print("\nSkala keyakinan gejala:")
    print("  1. Sangat Yakin (1.0)    2. Yakin (0.8)    3. Cukup Yakin (0.6)")
    print("  4. Sedikit Yakin (0.4)   5. Tidak Mengalami (0.0)\n")
    print("Memulai penelusuran (Depth-First Search)...\n")

    hasil_diagnosa = []

    for p_kode, p_data in knowledge_base.items():
        list_g_kode = list(p_data["gejala"].keys())

        cf_terkumpul, gejala_cocok = dfs_penelusuran_gejala(
            kode_penyakit=p_kode,
            list_gejala=list_g_kode,
            index=0,
            cf_terkumpul=[],
            gejala_cocok=[]
        )

        if len(cf_terkumpul) > 0:
            nilai_cf_akhir = hitung_cf_kombinasi(cf_terkumpul)
            total_gejala   = len(p_data["gejala"])
            rasio_gejala   = len(gejala_cocok) / total_gejala
            nilai_final    = nilai_cf_akhir * rasio_gejala
            persentase     = round(nilai_final * 100, 2)

            hasil_diagnosa.append({
                "kode_penyakit":        p_kode,
                "nama_penyakit":        p_data["nama_penyakit"],
                "gejala_match":         len(gejala_cocok),
                "total_gejala_penyakit": total_gejala,
                "keyakinan":            persentase,
                "rekomendasi":          p_data["rekomendasi"]
            })

    # ── Tampilkan hasil
    print("\n" + "=" * 65)
    print("PROSES DFS SELESAI. MENGHITUNG HASIL DIAGNOSA...")
    print("=" * 65)

    if not hasil_diagnosa:
        print("\nAnda tidak mengalami gejala yang mengarah pada gangguan jiwa dalam sistem kami.")
        print("Tetap jaga kesehatan mental Anda!")
        return

    hasil_diagnosa.sort(key=lambda x: x["keyakinan"], reverse=True)

    print("\nHASIL DIAGNOSA:\n")
    for idx, hasil in enumerate(hasil_diagnosa):
        print(f"{idx+1}. {hasil['nama_penyakit']} ({hasil['kode_penyakit']})")
        print(f"   Tingkat Keyakinan : {hasil['keyakinan']}%")
        print(f"   Gejala cocok      : {hasil['gejala_match']} dari {hasil['total_gejala_penyakit']}")
        print(f"   Rekomendasi       : {hasil['rekomendasi']}\n")

    print("=" * 65)
    print("CATATAN: Hasil ini adalah screening awal sistem pakar.")
    print("Segera hubungi profesional medis/psikiater untuk diagnosa resmi.")
    print("=" * 65)


if __name__ == "__main__":
    sistem_pakar()