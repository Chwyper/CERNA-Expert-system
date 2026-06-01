# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Penyakit(db.Model):
    __tablename__ = 'penyakit'
    kode = db.Column(db.String(10), primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    
    # Store rekomendasi as JSON string (since SQLite doesn't have native JSON before 3.9, 
    # and String/Text is universal). We'll handle serialize/deserialize in properties.
    rekomendasi_ringkas = db.Column(db.String(255), nullable=True)
    rekomendasi_detail = db.Column(db.Text, nullable=True) # JSON array
    rekomendasi_hubungi = db.Column(db.Text, nullable=True) # JSON array of dicts
    urgensi = db.Column(db.String(20), default='medium')

    # Relationship to PenyakitGejala
    gejala_rel = db.relationship('PenyakitGejala', back_populates='penyakit', cascade='all, delete-orphan')

    def set_detail(self, detail_list):
        self.rekomendasi_detail = json.dumps(detail_list)

    def get_detail(self):
        return json.loads(self.rekomendasi_detail) if self.rekomendasi_detail else []

    def set_hubungi(self, hubungi_list):
        self.rekomendasi_hubungi = json.dumps(hubungi_list)
        
    def get_hubungi(self):
        return json.loads(self.rekomendasi_hubungi) if self.rekomendasi_hubungi else []

    def to_dict(self):
        # Convert to dictionary exactly as KNOWLEDGE_BASE structure
        gejala_dict = {}
        for rel in self.gejala_rel:
            gejala_dict[rel.gejala_kode] = {
                "nama": rel.gejala.nama,
                "cf_pakar": rel.cf_pakar
            }
            
        return {
            "nama_penyakit": self.nama,
            "kategori": self.kategori,
            "deskripsi": self.deskripsi or "",
            "gejala": gejala_dict,
            "rekomendasi": {
                "ringkas": self.rekomendasi_ringkas or "",
                "detail": self.get_detail(),
                "hubungi": self.get_hubungi(),
                "urgensi": self.urgensi
            }
        }

class Gejala(db.Model):
    __tablename__ = 'gejala'
    kode = db.Column(db.String(10), primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    
    # Relationship to PenyakitGejala
    penyakit_rel = db.relationship('PenyakitGejala', back_populates='gejala', cascade='all, delete-orphan')

class PenyakitGejala(db.Model):
    __tablename__ = 'penyakit_gejala'
    penyakit_kode = db.Column(db.String(10), db.ForeignKey('penyakit.kode'), primary_key=True)
    gejala_kode = db.Column(db.String(10), db.ForeignKey('gejala.kode'), primary_key=True)
    cf_pakar = db.Column(db.Float, nullable=False, default=0.8)

    penyakit = db.relationship('Penyakit', back_populates='gejala_rel')
    gejala = db.relationship('Gejala', back_populates='penyakit_rel')
