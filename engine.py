"""
Mesin Inferensi (Inference Engine) untuk sistem pakar CERNA.
Berisi fungsi perhitungan Certainty Factor (CF) dan algoritma diagnosa.
"""
from models import Penyakit

def hitung_cf_kombinasi(cf_list):
    """
    Menghitung gabungan nilai CF menggunakan rumus CF Combine.
    """
    if not cf_list:
        return 0.0
    cf_lama = cf_list[0]
    for i in range(1, len(cf_list)):
        cf_baru = cf_list[i]
        cf_lama = cf_lama + cf_baru * (1 - cf_lama)
    return cf_lama


def jalankan_diagnosa(user_inputs, kode_penyakit_list=None):
    """
    Jalankan inference engine untuk menghitung probabilitas penyakit
    berdasarkan input gejala dari pengguna (user_inputs).
    
    Args:
        user_inputs (dict): Dictionary berupa { kode_gejala: nilai_cf_user }
        kode_penyakit_list (list): Opsional, daftar kode penyakit yang spesifik untuk difilter.
    """
    if kode_penyakit_list:
        penyakit_list = Penyakit.query.filter(Penyakit.kode.in_(kode_penyakit_list)).all()
    else:
        penyakit_list = Penyakit.query.all()
        
    hasil = []
    for p in penyakit_list:
        cf_terkumpul = []
        gejala_cocok = []
        
        for rel in p.gejala_rel:
            g_kode = rel.gejala_kode
            cf_pakar = rel.cf_pakar
            cf_user = float(user_inputs.get(g_kode, 0.0))
            
            if cf_user > 0.0:
                cf_gabungan = cf_pakar * cf_user
                cf_terkumpul.append(cf_gabungan)
                gejala_cocok.append(g_kode)
                
        if cf_terkumpul:
            nilai_cf_akhir = hitung_cf_kombinasi(cf_terkumpul)
            total_gejala = len(p.gejala_rel)
            rasio_gejala = len(gejala_cocok) / total_gejala
            nilai_final = nilai_cf_akhir * rasio_gejala
            persentase = round(nilai_final * 100, 2)
            
            hasil.append({
                "kode_penyakit": p.kode,
                "nama_penyakit": p.nama,
                "deskripsi": p.deskripsi,
                "gejala_match": len(gejala_cocok),
                "total_gejala": total_gejala,
                "keyakinan": persentase,
                "rekomendasi": {
                    "ringkas": p.rekomendasi_ringkas,
                    "detail": p.get_detail(),
                    "hubungi": p.get_hubungi(),
                    "urgensi": p.urgensi
                }
            })
            
    return hasil
