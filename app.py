"""
CERNA v2.0 — Sistem Pakar Diagnosa Kesehatan Mental (Database Edition)
Enhanced Flask App:
  - SQLite backend using Flask-SQLAlchemy (NLP-Ready)
  - Halaman Admin dengan CRUD ke Database
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os, json, random
from models import db, Penyakit, Gejala, PenyakitGejala, KataKunci
from seed_data import KATEGORI
from engine import jalankan_diagnosa
from nlp_engine import proses_pesan_chatbot, invalidate_keyword_cache

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
    import random
    data = request.get_json()
    pesan_asli = data.get("pesan", "")
    pesan = pesan_asli.lower().strip()
    
    if not pesan:
        return jsonify({"balasan": "Tolong masukkan cerita keluhan Anda.", "hasil": None})
        
    # ── TAHAP 3: DETEKSI JAWABAN YA/TIDAK (STATE MACHINE KONFIRMASI)
    konfirmasi_selesai = False
    if "tunggu_konfirmasi_gejala" in session and session["tunggu_konfirmasi_gejala"]:
        pending_g_kode = session["tunggu_konfirmasi_gejala"]
        pesan_tokens = pesan.replace(".", " ").replace(",", " ").split()
        
        is_yes = any(w in pesan_tokens for w in ["ya", "iya", "y", "benar", "betul", "sering", "banget", "hooh"])
        is_no = any(w in pesan_tokens for w in ["tidak", "enggak", "nggak", "bukan", "tdk", "gak", "jarang", "ngga"])
        
        if is_yes:
            gejala_terkumpul = session.get("gejala_terkumpul", {})
            gejala_terkumpul[pending_g_kode] = 0.8 # Anggap CF user = 0.8 jika "iya"
            session["gejala_terkumpul"] = gejala_terkumpul
            session.modified = True
            session.pop("tunggu_konfirmasi_gejala", None)
            user_inputs = {} # Lanjut diagnosa ulang tanpa NLP
            konfirmasi_selesai = True
        elif is_no:
            session.pop("tunggu_konfirmasi_gejala", None)
            user_inputs = {} # Lanjut diagnosa ulang dengan sisa memori
            konfirmasi_selesai = True
        else:
            # Jawaban ngambang, batalkan status konfirmasi dan proses normal
            session.pop("tunggu_konfirmasi_gejala", None)
            user_inputs = proses_pesan_chatbot(pesan_asli)
    else:
        # Memanggil mesin NLP fleksibel
        user_inputs = proses_pesan_chatbot(pesan_asli)
    
    # ── TAHAP 2: BASA-BASI AWAL (CHITCHAT) & LOGIKA FALLBACK
    # Hanya masuk ke sini jika BUKAN sedang menyelesaikan konfirmasi ya/tidak
    if not user_inputs and not konfirmasi_selesai and ("tunggu_konfirmasi_gejala" not in session):
        pesan_tokens = pesan.replace(".", " ").replace(",", " ").split()
        chitchat_words = ["halo", "hai", "p", "test", "tes", "curhat", "konsultasi", "pagi", "siang", "sore", "malam", "dok"]
        is_chitchat = any(w in pesan_tokens for w in chitchat_words) and len(pesan) < 30

        if is_chitchat:
            balasan_list = [
                "Halo! Aku siap mendengarkan cerita dan keluhanmu. Ada yang mengganggu fisik atau pikiran akhir-akhir ini?",
                "Hai! Jangan ragu untuk berbagi. Apa yang sedang kamu rasakan saat ini?",
                "Tentu, silakan curhat. Aku ada di sini untuk mendengarkan dan membantu menganalisis kondisimu. Mulai dari mana nih?"
            ]
            return jsonify({"status": "fallback", "balasan": random.choice(balasan_list), "hasil": None})
            
        # Fallback biasa jika tidak ada gejala tertangkap dan memori sesi kosong
        if "gejala_terkumpul" in session and session["gejala_terkumpul"]:
            return jsonify({
                "status": "fallback",
                "balasan": "Oke, aku catat. Silakan lanjutkan ceritamu, apakah ada keluhan lain yang menyertai?", 
                "hasil": None
            })
        else:
            return jsonify({
                "status": "fallback",
                "balasan": "Maaf, aku belum menangkap secara spesifik gejalanya. Bisa ceritakan lebih detail apa yang kamu rasakan secara fisik atau emosional?", 
                "hasil": None
            })
            
    # Menggabungkan gejala baru dengan memori sesi sebelumnya
    gejala_terkumpul = session.get("gejala_terkumpul", {})
    if user_inputs:
        for kode, cf in user_inputs.items():
            # Ambil nilai CF terbesar jika gejala sudah pernah disebutkan
            gejala_terkumpul[kode] = max(float(cf), float(gejala_terkumpul.get(kode, 0.0)))
            
        session["gejala_terkumpul"] = gejala_terkumpul
        session.modified = True

    # Jika tidak ada gejala sama sekali (dan bukan konfirmasi), tidak ada yang bisa didiagnosa
    if not gejala_terkumpul:
        return jsonify({
            "status": "fallback",
            "balasan": "Maaf, aku belum punya cukup informasi untuk melakukan analisis. Boleh ceritakan keluhan yang kamu rasakan?",
            "hasil": None
        })
        
    # Menghitung hasil diagnosa menggunakan keseluruhan gejala yang terkumpul
    hasil_diagnosa = jalankan_diagnosa(gejala_terkumpul)
    hasil_sorted = sorted(hasil_diagnosa, key=lambda x: x['keyakinan'], reverse=True)
    
    # ── TAHAP 3: LOGIKA VERIFIKASI (SEBELUM MUNCUL KARTU)
    if hasil_sorted and hasil_sorted[0]['keyakinan'] > 0:
        prediksi = hasil_sorted[0]
        sudah_ditanya = session.get("gejala_sudah_ditanya", [])
        
        # Batasi pertanyaan verifikasi maksimum 2 kali agar tidak looping
        MAX_VERIFIKASI = 2
        if (prediksi['keyakinan'] < 85 or prediksi['gejala_match'] < 3) and len(sudah_ditanya) < MAX_VERIFIKASI:
            penyakit_obj = db.session.get(Penyakit, prediksi['kode_penyakit'])
            
            gejala_tersisa = []
            for rel in penyakit_obj.gejala_rel:
                if rel.gejala_kode not in gejala_terkumpul and rel.gejala_kode not in sudah_ditanya:
                    gejala_tersisa.append((rel.gejala_kode, rel.gejala.nama))
                    
            if gejala_tersisa:
                g_kode_tanya, g_nama_tanya = gejala_tersisa[0]
                
                # Simpan ke state
                session["tunggu_konfirmasi_gejala"] = g_kode_tanya
                sudah_ditanya.append(g_kode_tanya)
                session["gejala_sudah_ditanya"] = sudah_ditanya
                session.modified = True
                
                balasan_verif = (
                    f"Aku perhatikan kamu mengalami beberapa keluhan yang mengarah ke hal tertentu. "
                    f"Agar analisaku lebih akurat, apakah akhir-akhir ini kamu juga sering merasa <b>{g_nama_tanya.lower()}</b>?"
                )
                return jsonify({
                    "status": "success",
                    "balasan": balasan_verif,
                    "hasil": None # Jangan munculkan kartu dulu
                })

        
        # Jika sudah memenuhi syarat atau tidak ada sisa gejala untuk ditanya, munculkan kartu final
        balasan = (
            f"Terima kasih sudah mau berbagi dan menjawab pertanyaanku. Dari semua yang kamu ceritakan, "
            f"analisisku menunjukkan indikasi kuat ke arah <b>{prediksi['nama_penyakit']}</b>.<br><br>"
            f"Yuk, lihat hasil diagnosis lengkap dan saran profesional untukmu pada kartu di bawah ini."
        )
        
        # Reset state verifikasi jika selesai
        session.pop("tunggu_konfirmasi_gejala", None)
        session.pop("gejala_sudah_ditanya", None)
        
        return jsonify({
            "status": "success",
            "balasan": balasan, 
            "hasil": prediksi
        })
    else:
        return jsonify({
            "status": "fallback",
            "balasan": "Aku mengerti apa yang kamu rasakan, namun gejalanya masih terlalu umum. Boleh ceritakan keluhan lain secara lebih spesifik?", 
            "hasil": None
        })

@app.route("/api/chat/reset", methods=["POST"])
def api_chat_reset():
    session.pop("gejala_terkumpul", None)
    session.pop("tunggu_konfirmasi_gejala", None)
    session.pop("gejala_sudah_ditanya", None)
    return jsonify({"status": "success", "message": "Memori sesi dan status konfirmasi dibersihkan."})

@app.route("/asesmen")
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

@app.route("/penyakit/<p_kode>")
def penyakit_detail(p_kode):
    penyakit = db.session.get(Penyakit, p_kode)
    if not penyakit:
        return redirect(url_for("index"))
    return render_template("detail_penyakit.html", penyakit=penyakit)


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

# (wraps sudah diimport di bagian atas file)

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
    p = db.get_or_404(Penyakit, p_kode)
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
    p = db.get_or_404(Penyakit, p_kode)
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
    p = db.get_or_404(Penyakit, p_kode)
    body = request.json
    nama = body.get("nama", "").strip()
    cf = float(body.get("cf_pakar", 0.8))
    g_kode = body.get("kode", "").strip().upper()
    
    if not nama or not g_kode:
        return jsonify({"error": "Kode dan nama gejala wajib diisi"}), 400
    if not (0.0 <= cf <= 1.0):
        return jsonify({"error": "CF harus antara 0.0 dan 1.0"}), 400
        
    g = db.session.get(Gejala, g_kode)
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


# ──────────────────────────────────────────────────────────────────────────────
# ADMIN - KATA KUNCI NLP (TAHAP 5)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/admin/kata_kunci")
@admin_required
def admin_kata_kunci():
    # Ambil semua kata kunci dan daftar gejala untuk form dropdown
    kata_kunci_list = KataKunci.query.join(Gejala).order_by(Gejala.kode, KataKunci.kata).all()
    gejala_list = Gejala.query.order_by(Gejala.kode).all()
    return render_template("admin_kata_kunci.html", kata_kunci_list=kata_kunci_list, gejala_list=gejala_list)

@app.route("/admin/kata_kunci/add", methods=["POST"])
@admin_required
def add_kata_kunci():
    try:
        data = request.form
        gejala_kode = data.get("gejala_kode")
        kata = data.get("kata", "").strip().lower()
        bobot = float(data.get("bobot", 0.8))
        
        if not gejala_kode or not kata:
            raise ValueError("Gejala dan Kata Kunci wajib diisi.")
            
        # Cek duplikat
        exists = KataKunci.query.filter_by(gejala_kode=gejala_kode, kata=kata).first()
        if exists:
            # Update bobot saja
            exists.bobot = bobot
        else:
            kw = KataKunci(gejala_kode=gejala_kode, kata=kata, bobot=bobot)
            db.session.add(kw)
            
        db.session.commit()
        invalidate_keyword_cache()  # Reset cache agar kata kunci baru langsung aktif
        return redirect(url_for("admin_kata_kunci"))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 400

@app.route("/admin/kata_kunci/delete/<int:kw_id>", methods=["POST"])
@admin_required
def delete_kata_kunci(kw_id):
    try:
        kw = db.get_or_404(KataKunci, kw_id)
        db.session.delete(kw)
        db.session.commit()
        invalidate_keyword_cache()  # Reset cache agar perubahan langsung efektif
        return redirect(url_for("admin_kata_kunci"))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 400


# ── API Admin: Hapus gejala dari penyakit
@app.route("/admin/api/penyakit/<p_kode>/gejala/<g_kode>", methods=["DELETE"])
@admin_required
def api_hapus_gejala(p_kode, g_kode):
    rel = PenyakitGejala.query.filter_by(penyakit_kode=p_kode, gejala_kode=g_kode).first_or_404()
    p = db.session.get(Penyakit, p_kode)
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
    if db.session.get(Penyakit, kode):
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
    p = db.get_or_404(Penyakit, p_kode)
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
            g = db.session.get(Gejala, g_kode)
            if not g:
                g = Gejala(kode=g_kode, nama=g_data["nama"])
                db.session.add(g)
            
            pg = PenyakitGejala(penyakit=p, gejala=g, cf_pakar=g_data["cf_pakar"])
            db.session.add(pg)
            
    db.session.commit()
    print("Database seeding completed.")

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL ERROR HANDLERS
# ──────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5000)
