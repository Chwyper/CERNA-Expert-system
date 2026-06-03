import json
from app import app
from models import db, Penyakit

def update_contacts():
    with app.app_context():
        penyakit_list = Penyakit.query.all()
        for p in penyakit_list:
            kontak = []
            if p.urgensi.lower() in ['tinggi', 'high', 'berat', 'sangat tinggi']:
                kontak = [
                    {
                        "siapa": "Layanan Darurat Kemenkes RI (119 ext 8)",
                        "alasan": "Tersedia 24 jam untuk dukungan krisis dan pencegahan risiko yang membahayakan nyawa."
                    },
                    {
                        "siapa": "Instalasi Gawat Darurat (IGD) RS Terdekat",
                        "alasan": "Untuk penanganan medis dan psikiatris segera jika kondisi sudah darurat."
                    },
                    {
                        "siapa": "Psikiater / Dokter Spesialis Kedokteran Jiwa (Sp.KJ)",
                        "alasan": "Dibutuhkan evaluasi komprehensif dan kemungkinan intervensi medikasi (obat)."
                    }
                ]
            else:
                kontak = [
                    {
                        "siapa": "Puskesmas dengan Fasilitas Psikolog",
                        "alasan": "Dapat diakses secara gratis/terjangkau menggunakan BPJS Kesehatan untuk konseling awal."
                    },
                    {
                        "siapa": "Yayasan Pulih",
                        "alasan": "Layanan konseling psikologis dengan biaya terjangkau (Telp: 021-78842580 atau via WhatsApp)."
                    },
                    {
                        "siapa": "Telemedisin (Halodoc / Alodokter / Riliv)",
                        "alasan": "Untuk konsultasi cepat dari rumah melalui chat atau video dengan Psikolog Klinis."
                    }
                ]
            
            p.set_hubungi(kontak)
            print(f"[OK] Diperbarui kontak untuk: {p.kode} - {p.nama} (Urgensi: {p.urgensi})")
        
        db.session.commit()
        print("\n🎉 Sukses! Seluruh data kontak telah diperbarui ke standar terbaru.")

if __name__ == "__main__":
    update_contacts()
