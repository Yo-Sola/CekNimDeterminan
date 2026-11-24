import importlib.util
import os
import sys

FILE_DAFTAR_NIM_DEFAULT = "daftar_nim.txt"
FILE_REKAP_OUTPUT = "rekap_hasil_cekall.txt"
FOLDER_HASIL_SATUAN = "hasil_cek"
POLA_DEFAULT = "4"
JUMLAH_SAMPEL_DEFAULT = 50000
SEED_ACAK = 2026

def muat_modul_cek():
    direktori_utama = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    kandidat_path = [
        os.path.join(direktori_utama, "cek.py"),
        os.path.join(direktori_utama, "modul", "cek.py"),
        os.path.join(direktori_utama, "cek", "cek.py"),
        os.path.join(direktori_utama, "engine", "cek.py")
    ]
    for akar, _, daftar_file in os.walk(direktori_utama):
        if "cek.py" in daftar_file:
            jalur_temuan = os.path.join(akar, "cek.py")
            if jalur_temuan not in kandidat_path:
                kandidat_path.append(jalur_temuan)

    for path_cek in kandidat_path:
        if os.path.isfile(path_cek):
            spec = importlib.util.spec_from_file_location("cek", path_cek)
            modul = importlib.util.module_from_spec(spec)
            sys.modules["cek"] = modul
            spec.loader.exec_module(modul)
            return modul, path_cek

    raise FileNotFoundError("File 'cek.py' tidak ditemukan di folder utama maupun sub-folder.")

def baca_daftar_nim(nama_file):
    if not os.path.isfile(nama_file):
        contoh_isi = "\n".join([
            "A11.2025.16563",
            "A11.2025.16562",
            "A11.2025.16285",
            "A11.2025.16560",
            "A11.2025.16561"
        ])
        with open(nama_file, "w", encoding="utf-8") as f:
            f.write(contoh_isi + "\n")
        print(f"[Info] File '{nama_file}' belum ada, dibuatkan contoh berisi 5 NIM otomatis.")

    daftar = []
    with open(nama_file, "r", encoding="utf-8") as f:
        for baris in f:
            bersih = baris.strip()
            if not bersih:
                continue
            daftar.append(bersih)
    return daftar

def format_baris_matriks_sebaris(mat):
    return "[" + "; ".join(" ".join(f"{v:2d}" for v in baris) for baris in mat) + "]"

def jalankan_batch(
    file_daftar=FILE_DAFTAR_NIM_DEFAULT,
    pilihan_pola=POLA_DEFAULT,
    jumlah_sampel=JUMLAH_SAMPEL_DEFAULT,
    file_rekap=FILE_REKAP_OUTPUT,
    folder_satuan=FOLDER_HASIL_SATUAN,
    seed=SEED_ACAK
):
    modul_cek, lokasi_cek = muat_modul_cek()
    daftar_nim = baca_daftar_nim(file_daftar)
    if not daftar_nim:
        raise ValueError(f"File '{file_daftar}' kosong. Masukkan minimal satu NIM.")

    pilihan = pilihan_pola.strip().upper()
    if pilihan not in ("3", "4", "34", "43", "SEMUA", "BOTH"):
        raise ValueError("Pilihan pola harus '3', '4', atau '34'.")

    print(f"\n[Engine] Memuat cek.py dari : {lokasi_cek}")
    print(f"[Input]  Total NIM dibaca   : {len(daftar_nim)} data dari '{file_daftar}'")
    print(f"[Mode]   Pola dipilih       : Pola {pilihan} | Percobaan/NIM = {jumlah_sampel:,}\n")

    semua_hasil = []
    for idx, teks_nim in enumerate(daftar_nim, 1):
        print(f"[{idx}/{len(daftar_nim)}] Memproses NIM: {teks_nim} ...", end=" ", flush=True)
        res = modul_cek.cek_satu_nim(
            nim_teks=teks_nim,
            pilihan_pola=pilihan,
            jumlah_sampel=jumlah_sampel,
            seed=seed,
            folder_output=folder_satuan,
            tampilkan_ke_layar=False
        )
        semua_hasil.append(res)
        ringkas_status = []
        for p_kode, h_pola in res["hasil_per_pola"].items():
            st = "BISA" if h_pola["bisa"] else "TIDAK BISA"
            ringkas_status.append(f"Pola {p_kode}={st} ({h_pola['persen_valid']:.2f}%)")
        print(" | ".join(ringkas_status))

    baris_rekap = []
    daftar_berhasil = []

    for res in semua_hasil:
        for p_kode, h_pola in res["hasil_per_pola"].items():
            status_teks = "BISA (VALID)" if h_pola["bisa"] else "TIDAK BISA"
            baris_rekap.append({
                "nim_input": res["nim_input"],
                "nim5": res["nim5"],
                "pola": f"Pola {p_kode}",
                "status": status_teks,
                "bisa": h_pola["bisa"],
                "valid_cnt": h_pola["det_valid"],
                "total_cnt": h_pola["jumlah_sampel"],
                "persen_valid": h_pola["persen_valid"],
                "det_nol": h_pola["det_nol"],
                "persen_nol": h_pola["persen_nol"],
                "alasan": h_pola["alasan_teoritis"],
                "file_laporan": res["file_laporan"]
            })
            if h_pola["bisa"] and h_pola["contoh_pertama_valid"] is not None:
                daftar_berhasil.append({
                    "nim_input": res["nim_input"],
                    "nim5": res["nim5"],
                    "pola": f"Pola {p_kode}",
                    "persen_valid": h_pola["persen_valid"],
                    "valid_cnt": h_pola["det_valid"],
                    "total_cnt": h_pola["jumlah_sampel"],
                    "contoh": h_pola["contoh_pertama_valid"]
                })

    total_pengujian = len(baris_rekap)
    total_bisa = sum(1 for r in baris_rekap if r["bisa"])
    total_tidak = total_pengujian - total_bisa

    out = []
    out.append("================================================================================================================")
    out.append("LAPORAN REKAPITULASI PENGECEKAN MASSAL DETERMINAN HILL CIPHER (MOD 26)")
    out.append("================================================================================================================")
    out.append(f"File Sumber NIM       : {file_daftar} ({len(daftar_nim)} NIM)")
    out.append(f"Pola Diuji            : Pola {pilihan} (3 = Acak 4x4, 4 = Acak 3x4, 34 = Keduanya)")
    out.append(f"Jumlah Percobaan/NIM  : {jumlah_sampel:,} matriks acak rentang 0-25")
    out.append(f"Folder Laporan Satuan : {folder_satuan}/")
    out.append(f"Ringkasan Hasil Akhir : {total_bisa} BISA (VALID) | {total_tidak} TIDAK BISA | Total Pengujian = {total_pengujian}")
    out.append("")

    out.append("1. TABEL DATA NIM & KEMUNGKINAN PELUANG DARI JUMLAH PERCOBAAN")
    out.append("----------------------------------------------------------------------------------------------------------------")
    header_1 = (
        f"{'No':>3} | {'NIM Input':<18} | {'5-Dig':<5} | {'Pola':<6} | "
        f"{'Status':<12} | {'Lolos / Percobaan':<17} | {'Peluang':>7} | {'Det=0':>6} | {'Keterangan'}"
    )
    garis_1 = (
        f"{'-'*3}-+-{'-'*18}-+-{'-'*5}-+-{'-'*6}-+-"
        f"{'-'*12}-+-{'-'*17}-+-{'-'*7}-+-{'-'*6}-+-{'-'*26}"
    )
    out.append(header_1)
    out.append(garis_1)

    for idx, item in enumerate(baris_rekap, 1):
        rasio_str = f"{item['valid_cnt']:,}/{item['total_cnt']:,}"
        peluang_str = f"{item['persen_valid']:6.2f}%"
        nol_str = f"{item['det_nol']:6d}"
        out.append(
            f"{idx:>3} | {item['nim_input']:<18} | {item['nim5']:<5} | {item['pola']:<6} | "
            f"{item['status']:<12} | {rasio_str:<17} | {peluang_str:>7} | {nol_str:>6} | {item['alasan']}"
        )
    out.append("")

    out.append("2. TABEL NIM YANG BERHASIL (BISA / VALID) BESERTA CONTOH MATRIKS KUNCI")
    out.append("----------------------------------------------------------------------------------------------------------------")
    if not daftar_berhasil:
        out.append("Tidak ada satupun NIM yang berhasil memenuhi syarat invers mod 26 pada pola yang dipilih.")
    else:
        header_2 = (
            f"{'No':>3} | {'NIM Input':<18} | {'5-Dig':<5} | {'Pola':<6} | "
            f"{'Peluang':>7} | {'Det(K)':>9} | {'Mod26':>5} | {'InvDet':>6} | {'Contoh Matriks Kunci K (5x5)'}"
        )
        garis_2 = (
            f"{'-'*3}-+-{'-'*18}-+-{'-'*5}-+-{'-'*6}-+-"
            f"{'-'*7}-+-{'-'*9}-+-{'-'*5}-+-{'-'*6}-+-{'-'*52}"
        )
        out.append(header_2)
        out.append(garis_2)

        for idx, b in enumerate(daftar_berhasil, 1):
            cth = b["contoh"]
            mat_1line = format_baris_matriks_sebaris(cth["matriks_K"])
            out.append(
                f"{idx:>3} | {b['nim_input']:<18} | {b['nim5']:<5} | {b['pola']:<6} | "
                f"{b['persen_valid']:6.2f}% | {cth['det']:>9d} | {cth['sisa']:>5d} | {cth['inv_det']:>6d} | {mat_1line}"
            )
        out.append("")
        out.append("3. RINCIAN BENTUK MATRIKS 5x5 & INVERS DEKRIPSI (K^-1 MOD 26) DARI CONTOH YANG BERHASIL")
        out.append("----------------------------------------------------------------------------------------------------------------")
        for idx, b in enumerate(daftar_berhasil, 1):
            cth = b["contoh"]
            out.append(
                f"[{idx}] NIM: {b['nim_input']} ({b['nim5']}) | {b['pola']} | "
                f"Peluang Valid: {b['persen_valid']:.2f}% ({b['valid_cnt']:,}/{b['total_cnt']:,}) | "
                f"det(K) = {cth['det']} | det % 26 = {cth['sisa']} | det^-1 mod 26 = {cth['inv_det']}"
            )
            out.append("    Matriks Kunci K (5x5):")
            out.extend(modul_cek.format_matriks(cth["matriks_K"], 2, "      "))
            out.append("    Matriks Invers Dekripsi K^-1 mod 26 (5x5):")
            out.extend(modul_cek.format_matriks(cth["matriks_inv"], 2, "      "))
            out.append("")

    out.append("================================================================================================================")
    teks_akhir = "\n".join(out)
    with open(file_rekap, "w", encoding="utf-8") as f:
        f.write(teks_akhir)

    print("\n" + teks_akhir)
    print(f"\n[Selesai! Laporan rekapitulasi tersimpan ke: {file_rekap}]")
    print(f"[Seluruh rincian satuan per NIM tersimpan di folder: {folder_satuan}/]")

def jalankan():
    print("=== SISTEM PENGECEKAN MASSAL DETERMINAN NIM (CEKALL) ===")
    print("  [3]  Pola Nomor 3 : NIM di Atas & Kiri        -> Area Acak 4x4 (16 sel)")
    print("  [4]  Pola Nomor 4 : NIM di Atas, Kiri, Bawah  -> Area Acak 3x4 (12 sel)")
    print("  [34] Uji Pola 3 dan Pola 4 sekaligus untuk setiap NIM")
    pola_in = input(f"Pilih pola ('3', '4', atau '34', ENTER = {POLA_DEFAULT}): ").strip() or POLA_DEFAULT
    file_in = input(f"Nama file .txt daftar NIM (ENTER = {FILE_DAFTAR_NIM_DEFAULT}): ").strip() or FILE_DAFTAR_NIM_DEFAULT
    sampel_in = input(f"Jumlah percobaan per NIM (ENTER = {JUMLAH_SAMPEL_DEFAULT}): ").strip()
    jml_sampel = int(sampel_in) if sampel_in else JUMLAH_SAMPEL_DEFAULT
    jalankan_batch(
        file_daftar=file_in,
        pilihan_pola=pola_in,
        jumlah_sampel=jml_sampel,
        file_rekap=FILE_REKAP_OUTPUT,
        folder_satuan=FOLDER_HASIL_SATUAN,
        seed=SEED_ACAK
    )

if __name__ == "__main__":
    jalankan()