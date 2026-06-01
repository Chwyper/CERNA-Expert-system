"""
CERNA v2.0 — Sistem Pakar Diagnosa Kesehatan Mental (Database Edition)
Enhanced Flask App:
  - SQLite backend using Flask-SQLAlchemy (NLP-Ready)
  - Halaman Admin dengan CRUD ke Database
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, json
from models import db, Penyakit, Gejala, PenyakitGejala, KataKunci
from seed_data import KATEGORI
from engine import jalankan_diagnosa
from nlp_engine import proses_pesan_chatbot

app = Flask(__name__)
app.secret_key = "cerna_secret_2026"   # Ganti dengan nilai random di produksi

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cerna.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ──────────────────────────────────────────────────────────────────────────────
# ROUTES UMUM (PENGGUNA)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pilih_metode")
def pilih_metode():
    return render_template("pilih_metode.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    pesan = data.get("pesan", "")
    
    if not pesan:
        return jsonify({"balasan": "Tolong ceritakan apa yang Anda rasakan.", "hasil": None})
        
    user_inputs = proses_pesan_chatbot(pesan)
    
    if not user_inputs:
        return jsonify({
            "balasan": "Saya kurang menangkap keluhan spesifik dari cerita Anda. Bisa diceritakan lebih detail mengenai gejala fisik atau emosi yang Anda rasakan?", 
            "hasil": None
        })
        
    hasil_diagnosa = jalankan_diagnosa(user_inputs)
    hasil_sorted = sorted(hasil_diagnosa, key=lambda x: x['keyakinan'], reverse=True)
    
    # Ambil hasil teratas jika keyakinannya cukup kuat (misal > 20%)
    if hasil_sorted and hasil_sorted[0]['keyakinan'] > 20.0:
        prediksi = hasil_sorted[0]
        balasan = (
            f"Dari cerita Anda, saya mendeteksi indikasi <b>{prediksi['nama_penyakit']}</b> "
            f"dengan tingkat kecocokan {prediksi['keyakinan']}%.<br><br>"
            f"Gejala yang tertangkap: {prediksi['gejala_match']} dari {prediksi['total_gejala']} gejala umum penyakit ini."
        )
        return jsonify({"balasan": balasan, "hasil": prediksi})
    else:
        return jsonify({
            "balasan": "Dari yang Anda ceritakan, gejalanya masih terlalu umum atau tidak spesifik. Boleh ceritakan keluhan lain yang lebih spesifik?", 
            "hasil": None
        })
def asesmen_manual():
    kategori_list = []
    for k_id, k_data in KATEGORI.items():
        penyakit_dalam = Penyakit.query.filter_by(kategori=k_id).all()
        if penyakit_dalam:
            # Count unique symptoms for this category
            gejala_set = set()
            for p in penyakit_dalam:
                for rel in p.gejala_rel:
                    gejala_set.add(rel.gejala_kode)
            jumlah_pertanyaan = len(gejala_set)
            perkiraan_waktu = f"{max(1, jumlah_pertanyaan // 3)}-{max(2, jumlah_pertanyaan // 2)} Menit"
            
            kategori_list.append({
                "id": k_id,
                "label": k_data["label"],
                "icon": k_data["icon"],
                "deskripsi": k_data["deskripsi"],
                "warna": k_data["warna"],
                "jumlah_pertanyaan": jumlah_pertanyaan,
                "perkiraan_waktu": perkiraan_waktu
            })
    return render_template("asesmen_manual.html", kategori_list=kategori_list)


@app.route("/asesmen/<kategori_id>")
def asesmen(kategori_id):
    if kategori_id not in KATEGORI:
        return redirect(url_for("index"))
        
    penyakit_dalam = Penyakit.query.filter_by(kategori=kategori_id).all()
    if not penyakit_dalam:
        return redirect(url_for("index"))

    gejala_list = {}
    for p in penyakit_dalam:
        for rel in p.gejala_rel:
            if rel.gejala_kode not in gejala_list:
                gejala_list[rel.gejala_kode] = rel.gejala.nama
                
    gejala_sorted = [{"kode": k, "nama": v} for k, v in sorted(gejala_list.items())]
    penyakit_kode_list = [p.kode for p in penyakit_dalam]
    kat_info = KATEGORI[kategori_id]
    
    penyakit_info = [
        {"kode": p.kode, "nama": p.nama, "deskripsi": p.deskripsi}
        for p in penyakit_dalam
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
    # List of penyakit to filter from the frontend payload
    penyakit_kode_list = data.pop("__penyakit_kode_list", None)
    
    hasil = jalankan_diagnosa(data, penyakit_kode_list)
    hasil.sort(key=lambda x: x["keyakinan"], reverse=True)
    return jsonify(hasil)


# ──────────────────────────────────────────────────────────────────────────────
# ROUTES ADMIN
# ──────────────────────────────────────────────────────────────────────────────
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

from functools import wraps

def admin_required(f):
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
    penyakit_all = Penyakit.query.all()
    for p in penyakit_all:
        summary.append({
            "kode": p.kode,
            "nama": p.nama,
            "kategori": KATEGORI.get(p.kategori, {}).get("label", p.kategori),
            "jumlah_gejala": len(p.gejala_rel),
            "urgensi": p.urgensi,
        })
    return render_template("admin_dashboard.html", penyakit_list=summary, kategori=KATEGORI)


@app.route("/admin/penyakit/<p_kode>")
@admin_required
def admin_detail_penyakit(p_kode):
    p = Penyakit.query.get_or_404(p_kode)
    return render_template(
        "admin_detail.html",
        p_kode=p.kode,
        p_data=p.to_dict(),
        kategori=KATEGORI
    )


# ── API Admin: Update nama/kategori/deskripsi penyakit
@app.route("/admin/api/penyakit/<p_kode>", methods=["PUT"])
@admin_required
def api_update_penyakit(p_kode):
    p = Penyakit.query.get_or_404(p_kode)
    body = request.json
    if "nama_penyakit" in body:
        p.nama = body["nama_penyakit"].upper().strip()
    if "kategori" in body:
        p.kategori = body["kategori"]
    if "deskripsi" in body:
        p.deskripsi = body["deskripsi"]
    if "rekomendasi_ringkas" in body:
        p.rekomendasi_ringkas = body["rekomendasi_ringkas"]
    if "urgensi" in body:
        p.urgensi = body["urgensi"]
        
    db.session.commit()
    return jsonify({"status": "ok", "kode": p_kode})


# ── API Admin: Update CF pakar suatu gejala
@app.route("/admin/api/penyakit/<p_kode>/gejala/<g_kode>", methods=["PUT"])
@admin_required
def api_update_gejala(p_kode, g_kode):
    rel = PenyakitGejala.query.filter_by(penyakit_kode=p_kode, gejala_kode=g_kode).first_or_404()
    body = request.json
    if "nama" in body:
        rel.gejala.nama = body["nama"]
    if "cf_pakar" in body:
        val = float(body["cf_pakar"])
        if not (0.0 <= val <= 1.0):
            return jsonify({"error": "CF harus antara 0.0 dan 1.0"}), 400
        rel.cf_pakar = round(val, 2)
        
    db.session.commit()
    return jsonify({"status": "ok", "gejala": {"nama": rel.gejala.nama, "cf_pakar": rel.cf_pakar}})


# ── API Admin: Tambah gejala baru ke penyakit
@app.route("/admin/api/penyakit/<p_kode>/gejala", methods=["POST"])
@admin_required
def api_tambah_gejala(p_kode):
    p = Penyakit.query.get_or_404(p_kode)
    body = request.json
    nama = body.get("nama", "").strip()
    cf = float(body.get("cf_pakar", 0.8))
    g_kode = body.get("kode", "").strip().upper()
    
    if not nama or not g_kode:
        return jsonify({"error": "Kode dan nama gejala wajib diisi"}), 400
    if not (0.0 <= cf <= 1.0):
        return jsonify({"error": "CF harus antara 0.0 dan 1.0"}), 400
        
    g = Gejala.query.get(g_kode)
    if not g:
        g = Gejala(kode=g_kode, nama=nama)
        db.session.add(g)
    else:
        # If user changed name, update globally
        g.nama = nama
        
    rel = PenyakitGejala.query.filter_by(penyakit_kode=p_kode, gejala_kode=g_kode).first()
    if not rel:
        rel = PenyakitGejala(penyakit=p, gejala=g, cf_pakar=round(cf, 2))
        db.session.add(rel)
    else:
        rel.cf_pakar = round(cf, 2)
        
    db.session.commit()
    return jsonify({"status": "ok", "kode": g_kode})


# ── API Admin: Hapus gejala dari penyakit
@app.route("/admin/api/penyakit/<p_kode>/gejala/<g_kode>", methods=["DELETE"])
@admin_required
def api_hapus_gejala(p_kode, g_kode):
    rel = PenyakitGejala.query.filter_by(penyakit_kode=p_kode, gejala_kode=g_kode).first_or_404()
    p = Penyakit.query.get(p_kode)
    if len(p.gejala_rel) <= 1:
        return jsonify({"error": "Minimal satu gejala harus ada"}), 400
        
    db.session.delete(rel)
    db.session.commit()
    return jsonify({"status": "ok"})


# ── API Admin: Tambah penyakit baru
@app.route("/admin/api/penyakit", methods=["POST"])
@admin_required
def api_tambah_penyakit():
    body = request.json
    kode = body.get("kode", "").strip().upper()
    nama = body.get("nama", "").strip().upper()
    kat = body.get("kategori", "mood")
    
    if not kode or not nama:
        return jsonify({"error": "Kode dan nama penyakit wajib diisi"}), 400
    if Penyakit.query.get(kode):
        return jsonify({"error": f"Kode {kode} sudah digunakan"}), 400
        
    p = Penyakit(
        kode=kode,
        nama=nama,
        kategori=kat,
        deskripsi=body.get("deskripsi", ""),
        rekomendasi_ringkas=body.get("rekomendasi_ringkas", ""),
        urgensi=body.get("urgensi", "medium")
    )
    p.set_detail([])
    p.set_hubungi([])
    db.session.add(p)
    db.session.commit()
    return jsonify({"status": "ok", "kode": kode})


# ── API Admin: Hapus penyakit
@app.route("/admin/api/penyakit/<p_kode>", methods=["DELETE"])
@admin_required
def api_hapus_penyakit(p_kode):
    p = Penyakit.query.get_or_404(p_kode)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"status": "ok"})


# ── API Admin: Get semua data (untuk export/review)
@app.route("/admin/api/export")
@admin_required
def api_export():
    penyakit_all = Penyakit.query.all()
    export_data = {p.kode: p.to_dict() for p in penyakit_all}
    return jsonify(export_data)


def seed_database():
    if Penyakit.query.first():
        return # Already seeded
    print("Seeding database...")
    from seed_data import KNOWLEDGE_BASE
    for p_kode, p_data in KNOWLEDGE_BASE.items():
        p = Penyakit(
            kode=p_kode,
            nama=p_data["nama_penyakit"],
            kategori=p_data["kategori"],
            deskripsi=p_data.get("deskripsi", ""),
            rekomendasi_ringkas=p_data["rekomendasi"].get("ringkas", ""),
            urgensi=p_data["rekomendasi"].get("urgensi", "medium")
        )
        p.set_detail(p_data["rekomendasi"].get("detail", []))
        p.set_hubungi(p_data["rekomendasi"].get("hubungi", []))
        db.session.add(p)
        
        for g_kode, g_data in p_data["gejala"].items():
            g = Gejala.query.get(g_kode)
            if not g:
                g = Gejala(kode=g_kode, nama=g_data["nama"])
                db.session.add(g)
            
            pg = PenyakitGejala(penyakit=p, gejala=g, cf_pakar=g_data["cf_pakar"])
            db.session.add(pg)
            
    db.session.commit()
    print("Database seeding completed.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5000)
