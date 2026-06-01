import json

# Pemetaan Gejala (ID) ke daftar sinonim/slang yang relevan (3-5 kata)
data_map = {
    # P01: ANSIETAS
    "G01": ["ngos-ngosan", "megap-megap", "sesak", "bengek"],
    "G02": ["deg-degan", "jantungan", "berdebar", "dag-dig-dug"],
    "G03": ["haus", "kering", "seret", "dahaga"],
    "G04": ["mager makan", "eneg", "gak selera", "ogah makan", "mual"],
    "G09": ["pusing", "mumet", "pening", "nyut-nyutan", "kliyengan"],
    "G10": ["insomnia", "begadang", "melek", "susah tidur"],
    "G11": ["keringetan", "lepek", "basah kuyup", "kemringet"],
    
    # P02: KETIDAKBERDAYAAN
    "G12": ["pasrah", "nyerah", "gak bisa apa-apa", "stuck"],
    "G13": ["gabut", "gak produktif", "useless", "ampas"],
    "G14": ["frustasi", "stres", "buntu", "mentok"],
    "G15": ["bingung", "insecure", "plin-plan", "bimbang"],
    "G16": ["males ngurus", "terlantar", "berantakan", "gak terawat"],
    "G17": ["kudet", "bodo amat", "apatis", "cuek"],
    "G18": ["diem aja", "pasif", "ngikut aja", "terserah"],
    "G19": ["mendam", "tertutup", "introvert", "sungkan curhat"],
    "G20": ["manja", "ketergantungan", "nempel terus", "baperan"],
    "G21": ["mengalah", "gampang ciut", "lembek", "penakut"],
    
    # P03: GANGGUAN CITRA TUBUH
    "G22": ["cacat", "buntung", "gak utuh", "amputasi"],
    "G23": ["berubah bentuk", "melar", "kurus kering", "kendor"],
    "G24": ["minder", "malu", "insecure fisik", "sengaja ditutupin"],
    "G25": ["benci kaca", "gak mau ngaca", "jijik", "buang muka"],
    "G26": ["geli", "ogah sentuh", "risih", "trauma"],
    "G27": ["ansos", "kuper", "ngurung diri", "anti sosial"],
    "G28": ["nyesal", "salah", "hina", "gak pede"],
    "G30": ["jelek", "burik", "buluk", "gak pantes"],
    "G31": ["galau", "overthinking", "ragu", "labil"],
    
    # P04: HARGA DIRI RENDAH SITUASIONAL
    "G32": ["ngatain diri", "merendah", "down", "pesimis"],
    "G33": ["ngeluh", "pesimis", "sambat", "negative vibes"],
    "G34": ["nyalahin diri", "guilt trip", "merasa berdosa", "aku yang salah"],
    "G35": ["takut salah", "bimbang", "gak berani milih", "overthink"],
    
    # P05: KEPUTUSASAAN
    "G36": ["hampa", "kosong", "hopeless", "gak ada masa depan", "gelap"],
    "G37": ["murung", "sedih", "nangis", "galau", "gloomy"],
    "G38": ["bisu", "diem", "sariawan", "gak mau ngomong", "bungkam"],
    "G39": ["datar", "blank", "muka tembok", "zombie"],
    "G40": ["menjauh", "ghosting", "ilang", "menyendiri", "tutup diri"],
    "G41": ["rakus", "binge eating", "gak nafsu", "lupa makan"],
    "G42": ["lemes", "loyo", "burnout", "capek mental", "gak mood"],
    
    # P06: HALUSINASI
    "G43": ["bisikan", "suara aneh", "halu", "mendengar sesuatu"],
    "G44": ["penampakan", "bayangan", "setan", "ilusi", "hantu"],
    "G45": ["ngomong dewe", "komat-kamit", "ngelantur", "ngigau"],
    "G46": ["resah", "gak tenang", "mondar-mandir", "cacingan"],
    "G47": ["melongo", "bengong", "tatapan kosong", "ngeblank"],
    "G48": ["gagal fokus", "gak nyambung", "tulalit", "telmi", "lemot"],
    
    # P07: WAHAM
    "G49": ["delusi", "ngaku nabi", "halu", "merasa hebat", "kesurupan"],
    "G50": ["paranoid", "parno", "curiga", "suudzon", "merasa diintai"],
    "G51": ["cerewet", "bawel", "ngelantur", "cerita ngidul", "hyper"],
    "G52": ["muka kaku", "tegang", "seram", "melotot"],
    
    # P08: PERILAKU KEKERASAN
    "G53": ["ngancam", "ngegas", "toxic", "misuh", "marah-marah"],
    "G54": ["mukul", "banting barang", "ngamuk", "tantrum", "anarkis"],
    "G55": ["mata melotot", "tangan ngepal", "muka merah", "emosi"],
    "G56": ["kaku", "siap berantem", "tegang", "otot kencang"],
    
    # P09: HARGA DIRI RENDAH KRONIS
    "G57": ["nunduk", "ciut", "lemah", "lemes"],
    "G58": ["buang muka", "takut natep", "gak berani liat", "malu"],
    "G59": ["bisik-bisik", "suara pelan", "lirih", "gak jelas"],
    "G60": ["ngekor", "plakat", "ngikut aja", "budak"],
    "G61": ["sampah", "gak guna", "beban keluarga", "pecundang", "payah"],
    
    # P10: ISOLASI SOSIAL
    "G62": ["pengen sendiri", "me time", "butuh waktu", "jauh-jauh"],
    "G63": ["nolak ajakan", "males nongkrong", "cancel", "skip"],
    "G64": ["cuek", "buang muka", "gak peduli", "dingin"],
    "G65": ["males bareng", "alergi orang", "benci keramaian", "phobia sosial"],
    
    # P11: DEFISIT PERAWATAN DIRI
    "G66": ["males mandi", "gak keramas", "bau", "dekil", "jorok"],
    "G67": ["rambut lepek", "ketombean", "kulit kusam", "bau badan"],
    "G68": ["kuku item", "kuku panjang", "kotor", "jijik"],
    "G69": ["baju lecek", "baju bau", "gembel", "lusuh", "acak-acakan"],
    "G70": ["makan jorok", "belepotan", "berantakan", "rakus"],
    
    # P12: RISIKO BUNUH DIRI
    "G71": ["mati aja", "bunuh diri", "suicide", "akhiri hidup", "capek hidup"],
    "G72": ["silet", "pisau", "obat tidur", "tali", "racun"],
    "G73": ["pamit", "wasiat", "titip pesan", "selamat tinggal", "maafin aku"],
    "G74": ["tiba-tiba happy", "aneh", "mood swing", "terlalu senang"],
    "G75": ["nyusahin", "beban", "mending aku gak ada", "mati lebih baik"]
}

hasil_json = []

for kode, kata_list in data_map.items():
    # Menentukan bobot, bervariasi antara 0.7 - 0.95 agar lebih realistis
    bobot = 0.85
    for kata in kata_list:
        hasil_json.append({
            "gejala_kode": kode,
            "kata": kata,
            "bobot": bobot
        })

# Simpan ke file
with open("keyword_for_inject2.json", "w", encoding="utf-8") as f:
    json.dump(hasil_json, f, indent=4, ensure_ascii=False)

print(f"Berhasil membuat keyword_for_inject2.json dengan {len(hasil_json)} kata kunci.")
