import math
import os
import random

NIM_DEFAULT = "16563"
JUMLAH_SAMPEL_DEFAULT = 50000
SEED_ACAK = 2026
POLA_DEFAULT = "3"
FOLDER_OUTPUT_SATUAN = "hasil_cek"

def ekstrak_5_digit_nim(teks_nim):
    bagian_utama = teks_nim.split("-")[0].split("#")[0].strip()
    digit_saja = "".join([c for c in bagian_utama if c.isdigit()])
    if len(digit_saja) < 5:
        raise ValueError(f"NIM '{teks_nim}' harus mengandung minimal 5 digit angka.")
    nim5 = digit_saja[-5:]
    nama_file_id = "".join([c if c.isalnum() else "_" for c in bagian_utama])
    return bagian_utama, nim5, nama_file_id

def determinan_eksak(mat):
    n = len(mat)
    if n == 1:
        return mat[0][0]
    if n == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    total = 0
    for c in range(n):
        sub = [baris[:c] + baris[c + 1:] for baris in mat[1:]]
        tanda = -1 if (c % 2 == 1) else 1
        total += tanda * mat[0][c] * determinan_eksak(sub)
    return total

def invers_modular(a, m=26):
    a_mod = a % m
    for x in range(1, m):
        if (a_mod * x) % m == 1:
            return x
    return None

def hitung_invers_matriks_mod26(K):
    n = len(K)
    det = determinan_eksak(K)
    det_mod = det % 26
    inv_det = invers_modular(det_mod, 26)
    if inv_det is None:
        return None
    adj = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            minor = [baris[:c] + baris[c + 1:] for idx, baris in enumerate(K) if idx != r]
            tanda = -1 if ((r + c) % 2 == 1) else 1
            adj[c][r] = (tanda * determinan_eksak(minor)) % 26
    return [[(inv_det * adj[r][c]) % 26 for c in range(n)] for r in range(n)]

def format_matriks(mat, lebar=2, indent="   "):
    return [f"{indent}[ " + " ".join(f"{val:>{lebar}d}" for val in baris) + " ]" for baris in mat]

def bangun_matriks_5x5(nim5, nilai_acak, pola):
    x = [int(d) for d in nim5]
    K = [[0] * 5 for _ in range(5)]
    for j in range(5):
        K[0][j] = x[j]
        K[j][0] = x[j]
    if pola == "3":
        idx = 0
        for r in range(1, 5):
            for c in range(1, 5):
                K[r][c] = nilai_acak[idx]
                idx += 1
    else:
        for j in range(5):
            K[4][j] = x[4 - j]
        idx = 0
        for r in range(1, 4):
            for c in range(1, 5):
                K[r][c] = nilai_acak[idx]
                idx += 1
    return K

def siapkan_ekspansi_pola3(nim5):
    x = [int(d) for d in nim5]
    suku = []
    for c0 in range(5):
        if x[c0] == 0:
            continue
        tanda = -1 if (c0 % 2 == 1) else 1
        koef = tanda * x[c0]
        kol_sisa = [c for c in range(5) if c != c0]
        suku.append((koef, kol_sisa))
    return [x[1], x[2], x[3], x[4]], suku

def det_4x4(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33):
    d0 = m11 * (m22 * m33 - m23 * m32) - m12 * (m21 * m33 - m23 * m31) + m13 * (m21 * m32 - m22 * m31)
    d1 = m10 * (m22 * m33 - m23 * m32) - m12 * (m20 * m33 - m23 * m30) + m13 * (m20 * m32 - m22 * m30)
    d2 = m10 * (m21 * m33 - m23 * m31) - m11 * (m20 * m33 - m23 * m30) + m13 * (m20 * m31 - m21 * m30)
    d3 = m10 * (m21 * m32 - m22 * m31) - m11 * (m20 * m32 - m22 * m30) + m12 * (m20 * m31 - m21 * m30)
    return m00 * d0 - m01 * d1 + m02 * d2 - m03 * d3

def det_cepat_pola3(col0, suku, vals):
    total = 0
    for koef, cols in suku:
        c0, c1, c2, c3 = cols
        m00 = col0[0] if c0 == 0 else vals[c0 - 1]
        m10 = col0[1] if c0 == 0 else vals[4 + c0 - 1]
        m20 = col0[2] if c0 == 0 else vals[8 + c0 - 1]
        m30 = col0[3] if c0 == 0 else vals[12 + c0 - 1]

        m01 = col0[0] if c1 == 0 else vals[c1 - 1]
        m11 = col0[1] if c1 == 0 else vals[4 + c1 - 1]
        m21 = col0[2] if c1 == 0 else vals[8 + c1 - 1]
        m31 = col0[3] if c1 == 0 else vals[12 + c1 - 1]

        m02 = col0[0] if c2 == 0 else vals[c2 - 1]
        m12 = col0[1] if c2 == 0 else vals[4 + c2 - 1]
        m22 = col0[2] if c2 == 0 else vals[8 + c2 - 1]
        m32 = col0[3] if c2 == 0 else vals[12 + c2 - 1]

        m03 = col0[0] if c3 == 0 else vals[c3 - 1]
        m13 = col0[1] if c3 == 0 else vals[4 + c3 - 1]
        m23 = col0[2] if c3 == 0 else vals[8 + c3 - 1]
        m33 = col0[3] if c3 == 0 else vals[12 + c3 - 1]

        total += koef * det_4x4(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33)
    return total

def siapkan_ekspansi_pola4(nim5):
    x = [int(d) for d in nim5]
    r0 = x[:]
    r4 = x[::-1]
    col0 = [x[1], x[2], x[3]]
    suku = []
    for c0 in range(5):
        for c4 in range(5):
            if c0 == c4:
                continue
            kol_sisa = [c for c in range(5) if c != c0 and c != c4]
            pos_c4 = sum(1 for c in range(5) if c != c0 and c < c4)
            tanda = ((-1) ** c0) * ((-1) ** (3 + pos_c4))
            koef = tanda * r0[c0] * r4[c4]
            if koef != 0:
                suku.append((koef, kol_sisa))
    return col0, suku

def det_cepat_pola4(col0, suku, vals):
    total = 0
    for koef, cols in suku:
        ca, cb, cc = cols
        a0 = col0[0] if ca == 0 else vals[ca - 1]
        a1 = col0[1] if ca == 0 else vals[4 + ca - 1]
        a2 = col0[2] if ca == 0 else vals[8 + ca - 1]

        b0 = col0[0] if cb == 0 else vals[cb - 1]
        b1 = col0[1] if cb == 0 else vals[4 + cb - 1]
        b2 = col0[2] if cb == 0 else vals[8 + cb - 1]

        d0 = col0[0] if cc == 0 else vals[cc - 1]
        d1 = col0[1] if cc == 0 else vals[4 + cc - 1]
        d2 = col0[2] if cc == 0 else vals[8 + cc - 1]

        det3 = (
            a0 * (b1 * d2 - b2 * d1)
            - b0 * (a1 * d2 - a2 * d1)
            + d0 * (a1 * b2 - a2 * b1)
        )
        total += koef * det3
    return total

def simulasi_satu_pola(nim5, pola, jumlah_sampel, seed):
    x = [int(d) for d in nim5]
    b1 = x[:]
    b5 = x[::-1]
    b1_plus_b5 = [b1[i] + b5[i] for i in range(5)]
    terkunci_genap = (pola == "4") and all(v % 2 == 0 for v in b1_plus_b5)

    jumlah_sel = 16 if pola == "3" else 12
    ruang_semesta = 26 ** jumlah_sel
    rng = random.Random(seed)

    distribusi_sisa = {r: 0 for r in range(26)}
    perwakilan_sisa = {}
    contoh_pertama_valid = None

    det_nol = 0
    det_genap = 0
    det_kelipatan_13 = 0
    det_ganjil_13 = 0
    det_valid = 0

    if pola == "3":
        col0, suku = siapkan_ekspansi_pola3(nim5)
        for _ in range(jumlah_sampel):
            vals = [rng.randint(0, 25) for _ in range(16)]
            det = det_cepat_pola3(col0, suku, vals)
            sisa = det % 26
            distribusi_sisa[sisa] += 1
            if det == 0:
                det_nol += 1
            if sisa % 2 == 0:
                det_genap += 1
            if sisa % 13 == 0:
                det_kelipatan_13 += 1
            if sisa == 13:
                det_ganjil_13 += 1
            if math.gcd(sisa, 26) == 1:
                det_valid += 1
                if contoh_pertama_valid is None:
                    K_val = bangun_matriks_5x5(nim5, vals, "3")
                    inv_d = invers_modular(sisa, 26)
                    inv_K = hitung_invers_matriks_mod26(K_val)
                    contoh_pertama_valid = {
                        "matriks_K": K_val,
                        "matriks_inv": inv_K,
                        "det": det,
                        "sisa": sisa,
                        "inv_det": inv_d
                    }
            if sisa not in perwakilan_sisa:
                K = bangun_matriks_5x5(nim5, vals, "3")
                perwakilan_sisa[sisa] = (K, det, sisa)
    else:
        col0, suku = siapkan_ekspansi_pola4(nim5)
        for _ in range(jumlah_sampel):
            vals = [rng.randint(0, 25) for _ in range(12)]
            det = det_cepat_pola4(col0, suku, vals)
            sisa = det % 26
            distribusi_sisa[sisa] += 1
            if det == 0:
                det_nol += 1
            if sisa % 2 == 0:
                det_genap += 1
            if sisa % 13 == 0:
                det_kelipatan_13 += 1
            if sisa == 13:
                det_ganjil_13 += 1
            if math.gcd(sisa, 26) == 1:
                det_valid += 1
                if contoh_pertama_valid is None:
                    K_val = bangun_matriks_5x5(nim5, vals, "4")
                    inv_d = invers_modular(sisa, 26)
                    inv_K = hitung_invers_matriks_mod26(K_val)
                    contoh_pertama_valid = {
                        "matriks_K": K_val,
                        "matriks_inv": inv_K,
                        "det": det,
                        "sisa": sisa,
                        "inv_det": inv_d
                    }
            if sisa not in perwakilan_sisa:
                K = bangun_matriks_5x5(nim5, vals, "4")
                perwakilan_sisa[sisa] = (K, det, sisa)

    sapuan_0_25 = []
    for dasar in range(26):
        vals_sapuan = [((dasar + i * (dasar + 3) + (i // 3)) % 26) for i in range(jumlah_sel)]
        K_sap = bangun_matriks_5x5(nim5, vals_sapuan, pola)
        det_sap = determinan_eksak(K_sap)
        sisa_sap = det_sap % 26
        val_sap = math.gcd(sisa_sap, 26) == 1
        sapuan_0_25.append((dasar, det_sap, sisa_sap, val_sap))

    if pola == "3":
        alasan_teoritis = "Lolos (Blok 4x4 Bawah Bebas)"
    elif terkunci_genap:
        alasan_teoritis = "Terkunci Genap (B1+B5 Genap)"
    else:
        alasan_teoritis = "Lolos (B1+B5 Ada Ganjil)"

    return {
        "pola": pola,
        "bisa": det_valid > 0,
        "persen_valid": (det_valid / jumlah_sampel) * 100,
        "persen_genap": (det_genap / jumlah_sampel) * 100,
        "persen_nol": (det_nol / jumlah_sampel) * 100,
        "alasan_teoritis": alasan_teoritis,
        "contoh_pertama_valid": contoh_pertama_valid,
        "jumlah_sel": jumlah_sel,
        "ruang_semesta": ruang_semesta,
        "b1": b1,
        "b5": b5,
        "b1_plus_b5": b1_plus_b5,
        "terkunci_genap": terkunci_genap,
        "jumlah_sampel": jumlah_sampel,
        "det_valid": det_valid,
        "det_genap": det_genap,
        "det_nol": det_nol,
        "det_kelipatan_13": det_kelipatan_13,
        "det_ganjil_13": det_ganjil_13,
        "distribusi_sisa": distribusi_sisa,
        "perwakilan_sisa": perwakilan_sisa,
        "sapuan_0_25": sapuan_0_25
    }

def susun_laporan_pola(nim_label, nim5, hasil):
    x = [int(d) for d in nim5]
    pola = hasil["pola"]
    jumlah_sampel = hasil["jumlah_sampel"]
    jumlah_sel = hasil["jumlah_sel"]
    ruang_semesta = hasil["ruang_semesta"]

    persen_valid = hasil["persen_valid"]
    persen_genap = hasil["persen_genap"]
    persen_nol = hasil["persen_nol"]
    persen_13 = (hasil["det_kelipatan_13"] / jumlah_sampel) * 100
    persen_ganjil_13 = (hasil["det_ganjil_13"] / jumlah_sampel) * 100

    out = []
    out.append("================================================================================")
    out.append(f"ANALISIS PELUANG DETERMINAN (MOD 26) - POLA {pola} - NIM: {nim_label} ({nim5})")
    out.append("================================================================================")
    if pola == "3":
        out.append("Pola Matriks Kunci  : POLA 3 (NIM di Atas & Kiri | Area Acak = 4x4 = 16 sel)")
        out.append("Layout Matriks 5x5  :")
        out.append(f"   [ {x[0]}  {x[1]}  {x[2]}  {x[3]}  {x[4]} ]")
        out.append(f"   [ {x[1]}  ?  ?  ?  ? ]")
        out.append(f"   [ {x[2]}  ?  ?  ?  ? ]  <-- Area Acak 4x4 (16 sel, rentang 0-25)")
        out.append(f"   [ {x[3]}  ?  ?  ?  ? ]")
        out.append(f"   [ {x[4]}  ?  ?  ?  ? ]")
    else:
        out.append("Pola Matriks Kunci  : POLA 4 (NIM di Atas, Kiri, Bawah | Area Acak = 3x4 = 12 sel)")
        out.append("Layout Matriks 5x5  :")
        out.append(f"   [ {x[0]}  {x[1]}  {x[2]}  {x[3]}  {x[4]} ]")
        out.append(f"   [ {x[1]}  ?  ?  ?  ? ]")
        out.append(f"   [ {x[2]}  ?  ?  ?  ? ]  <-- Area Acak 3x4 (12 sel, rentang 0-25)")
        out.append(f"   [ {x[3]}  ?  ?  ?  ? ]")
        out.append(f"   [ {x[4]}  {x[3]}  {x[2]}  {x[1]}  {x[0]} ]")

    out.append(f"Ruang Semesta Penuh : 26^{jumlah_sel} = {ruang_semesta:,} kemungkinan")
    out.append(f"Jumlah Sampel Acak  : {jumlah_sampel:,} matriks acak seragam (rentang 0-25)")
    out.append("")

    out.append("1. ANALISIS TEORITIS PARITAS BARIS NIM")
    out.append("--------------------------------------------------------------------------------")
    if pola == "3":
        out.append("- Pada Pola 3, hanya Baris 1 dan Kolom 1 yang dikunci oleh digit NIM, sedangkan")
        out.append("  blok 4x4 (Baris 2 s/d 5, Kolom 2 s/d 5) bebas diisi angka 0-25.")
        out.append("- Tidak ada penguncian paritas baris atas-bawah, sehingga SEMUA NIM dapat")
        out.append("  menghasilkan matriks kunci valid yang memiliki invers mod 26.")
    else:
        b1 = hasil["b1"]
        b5 = hasil["b5"]
        b1_plus_b5 = hasil["b1_plus_b5"]
        out.append(f"- Baris 1 (B1)        = {b1}")
        out.append(f"- Baris 5 (B5)        = {b5}")
        out.append(f"- Operasi B5' = B1+B5 = {b1_plus_b5}")
        out.append(f"- Paritas B5' % 2     = {[v % 2 for v in b1_plus_b5]} (0=Genap, 1=Ganjil)")
        if hasil["terkunci_genap"]:
            out.append("- KESIMPULAN TEORITIS : TIDAK VALID (0.00% Peluang Invers).")
            out.append(f"  Seluruh elemen B1+B5 = {b1_plus_b5} habis dibagi 2 (genap), sehingga det(K)")
            out.append("  selalu genap untuk seluruh 26^12 kombinasi dan gcd(det % 26, 26) != 1.")
        else:
            out.append("- KESIMPULAN TEORITIS : VALID (Memiliki Peluang Invers Mod 26).")
            out.append("  B1+B5 memuat angka ganjil sehingga determinan dapat bernilai ganjil & koprima 26.")
    out.append("")

    out.append(f"2. REKAPITULASI PERSENTASE PELUANG (DARI {jumlah_sampel:,} SAMPEL ACAK)")
    out.append("--------------------------------------------------------------------------------")
    out.append(f"- VALID (Punya Invers Mod 26 / gcd=1) : {hasil['det_valid']:6d} / {jumlah_sampel}  ({persen_valid:6.2f}%)")
    out.append(f"- TIDAK VALID Total (gcd != 1)        : {jumlah_sampel - hasil['det_valid']:6d} / {jumlah_sampel}  ({100.0 - persen_valid:6.2f}%)")
    out.append(f"    * Rincian Determinan Genap        : {hasil['det_genap']:6d} / {jumlah_sampel}  ({persen_genap:6.2f}%)")
    out.append(f"    * Rincian Determinan == 0 (Eksak) : {hasil['det_nol']:6d} / {jumlah_sampel}  ({persen_nol:6.3f}%)")
    out.append(f"    * Rincian Kelipatan 13 (Semua)    : {hasil['det_kelipatan_13']:6d} / {jumlah_sampel}  ({persen_13:6.2f}%)")
    out.append(f"    * Rincian Ganjil Kelipatan 13     : {hasil['det_ganjil_13']:6d} / {jumlah_sampel}  ({persen_ganjil_13:6.2f}%)")
    out.append("")

    out.append("3. TABEL DISTRIBUSI & PERSENTASE TIAP SISA HASIL (det % 26) DARI 00 s/d 25")
    out.append("--------------------------------------------------------------------------------")
    out.append("Sisa (det%26) | Status      | Jumlah Sampel | Persentase | Grafik Proporsi")
    out.append("--------------+-------------+---------------+------------+------------------------")
    for r_val in range(26):
        cnt = hasil["distribusi_sisa"][r_val]
        pct = (cnt / jumlah_sampel) * 100
        is_valid = math.gcd(r_val, 26) == 1
        status_str = "VALID      " if is_valid else "TIDAK VALID"
        bar = "=" * int(round(pct * 2.5))
        out.append(f"   Sisa {r_val:02d}    | {status_str} | {cnt:13,d} |   {pct:6.2f}%  | {bar}")
    out.append("")

    out.append("4. SAPUAN BERTAHAP ANGKA DASAR 0 SAMPAI 25 (26 LANGKAH PERWAKILAN)")
    out.append("--------------------------------------------------------------------------------")
    for dasar, det_sap, sisa_sap, val_sap in hasil["sapuan_0_25"]:
        out.append(f"Angka Dasar {dasar:02d} -> det = {det_sap:10d} | det % 26 = {sisa_sap:02d} | Valid = {val_sap}")
    out.append("")

    sisa_valid_list = [r for r in range(26) if math.gcd(r, 26) == 1]
    out.append("5. MATRIKS PERWAKILAN UNTUK SETIAP SISA VALID (12 KELAS VALID MOD 26)")
    out.append("--------------------------------------------------------------------------------")
    if hasil["terkunci_genap"]:
        out.append(f"KETERANGAN: Tidak ada perwakilan 12 kelas valid karena NIM {nim5} pada Pola 4")
        out.append("terkunci pada determinan genap (0.00% valid). Berikut perwakilan sisa genap:")
        for r_val in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]:
            if r_val in hasil["perwakilan_sisa"]:
                K, det_asli, sisa = hasil["perwakilan_sisa"][r_val]
                out.append(f"Perwakilan Sisa {sisa:02d} (det = {det_asli}, gcd({sisa},26) = {math.gcd(sisa, 26)}):")
                out.extend(format_matriks(K, 2))
    else:
        for r_val in sisa_valid_list:
            if r_val in hasil["perwakilan_sisa"]:
                K, det_asli, sisa = hasil["perwakilan_sisa"][r_val]
                inv_d = invers_modular(sisa, 26)
                inv_K = hitung_invers_matriks_mod26(K)
                out.append(f"Kelas Valid Sisa {sisa:02d} | det(K) = {det_asli} | det^-1 mod 26 = {inv_d}")
                out.append("  Matriks Kunci K:")
                out.extend(format_matriks(K, 2))
                out.append("  Matriks Invers Dekripsi K^-1 mod 26:")
                out.extend(format_matriks(inv_K, 2))
                out.append("")
    out.append("================================================================================")
    return "\n".join(out)

def cek_satu_nim(
    nim_teks=NIM_DEFAULT,
    pilihan_pola=POLA_DEFAULT,
    jumlah_sampel=JUMLAH_SAMPEL_DEFAULT,
    seed=SEED_ACAK,
    folder_output=FOLDER_OUTPUT_SATUAN,
    tampilkan_ke_layar=True
):
    nim_label, nim5, nama_file_id = ekstrak_5_digit_nim(nim_teks)
    pilihan = pilihan_pola.strip().upper()
    os.makedirs(folder_output, exist_ok=True)
    nama_file = os.path.join(folder_output, f"peluang_determinan_{nama_file_id}.txt")

    hasil_per_pola = {}
    if pilihan in ("34", "43", "SEMUA", "BOTH"):
        h3 = simulasi_satu_pola(nim5, "3", jumlah_sampel, seed)
        h4 = simulasi_satu_pola(nim5, "4", jumlah_sampel, seed)
        hasil_per_pola["3"] = h3
        hasil_per_pola["4"] = h4

        ringkasan = []
        ringkasan.append("================================================================================")
        ringkasan.append(f"PERBANDINGAN LANGSUNG POLA 3 (4x4) VS POLA 4 (3x4) - NIM: {nim_label} ({nim5})")
        ringkasan.append("================================================================================")
        ringkasan.append(f"Pola 3 (Atas & Kiri = NIM | Acak 4x4)        : Valid = {h3['det_valid']:,}/{jumlah_sampel:,} ({h3['persen_valid']:.2f}%)")
        ringkasan.append(f"Pola 4 (Atas, Kiri, Bawah = NIM | Acak 3x4) : Valid = {h4['det_valid']:,}/{jumlah_sampel:,} ({h4['persen_valid']:.2f}%)")
        ringkasan.append("================================================================================")
        ringkasan.append("")

        teks_laporan = "\n".join(ringkasan) + susun_laporan_pola(nim_label, nim5, h3) + "\n\n" + susun_laporan_pola(nim_label, nim5, h4)
    elif pilihan in ("3", "4"):
        h = simulasi_satu_pola(nim5, pilihan, jumlah_sampel, seed)
        hasil_per_pola[pilihan] = h
        teks_laporan = susun_laporan_pola(nim_label, nim5, h)
    else:
        raise ValueError("Pilihan pola harus '3', '4', atau '34'.")

    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(teks_laporan)

    if tampilkan_ke_layar:
        print(teks_laporan)
        print(f"\n[Laporan satuan tersimpan ke: {nama_file}]")

    return {
        "nim_input": nim_teks.strip(),
        "nim_label": nim_label,
        "nim5": nim5,
        "file_laporan": nama_file,
        "hasil_per_pola": hasil_per_pola
    }

def jalankan():
    print("=== PROGRAM CEK DETERMINAN SATUAN (POLA 3 & POLA 4) ===")
    print("  [3]  Pola Nomor 3 : NIM di Atas & Kiri        -> Area Acak 4x4 (16 sel)")
    print("  [4]  Pola Nomor 4 : NIM di Atas, Kiri, Bawah  -> Area Acak 3x4 (12 sel)")
    print("  [34] Bandingkan Pola 3 dan Pola 4 sekaligus")
    pilihan_in = input(f"Pilih pola ('3', '4', atau '34', ENTER = {POLA_DEFAULT}): ").strip() or POLA_DEFAULT
    nim_in = input(f"Masukkan NIM atau 5 digit akhir NIM (ENTER = {NIM_DEFAULT}): ").strip() or NIM_DEFAULT
    sampel_in = input(f"Masukkan jumlah sampel acak (ENTER = {JUMLAH_SAMPEL_DEFAULT}): ").strip()
    jml_sampel = int(sampel_in) if sampel_in else JUMLAH_SAMPEL_DEFAULT
    cek_satu_nim(
        nim_teks=nim_in,
        pilihan_pola=pilihan_in,
        jumlah_sampel=jml_sampel,
        seed=SEED_ACAK,
        folder_output=FOLDER_OUTPUT_SATUAN,
        tampilkan_ke_layar=True
    )

if __name__ == "__main__":
    jalankan()