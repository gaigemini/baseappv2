import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM

ollama_llm = LocalLLM(api_base="http://202.149.64.34:11434/v1", model="qwen2.5:latest")

# Data Dummy (Array)
data_dummy = [
    {
        "_id": "0271cdc2-faad-4181-91b4-ca892d218c4d",
        "code": "ALKS001493",
        "details": {
            "bahan_aktif": [],
            "dosis": [],
            "efek_samping": [],
            "indikasi": ["suntikan intramuskular"],
            "interaksi_obat": [],
            "jenis_obat": [],
            "kategori_obat": ["alat medis"],
            "kontraindikasi": [],
            "lama_penyimpanan": [],
            "mekanisme_kerja": ["memfasilitasi pemberian obat secara intramuskular"],
            "nama_dagang": [],
            "nama_obat": "JARUM OTOT 13",
            "overdosis": [],
            "penjelasan_dosis": [],
            "perhatian": ["hindari penggunaan kembali"],
            "peringatan": ["gunakan sesuai petunjuk medis"],
            "persetujuan_regulator": [],
            "petunjuk_penyimpanan": ["simpan di tempat kering dan sejuk"],
            "produsen": [],
            "waktu_kerja": []
        },
        "name": "JARUM OTOT 13 [12]",
        "satuan": "Piece"
    },
    {
        "_id": "002fc881-05f6-4b75-8440-86fbbfb4854f",
        "code": "OBAT001269",
        "details": {
            "bahan_aktif": ["Benzydamine"],
            "dosis": ["Dewasa dan anak di atas 6 tahun: berkumur 15 ml larutan 2-3 kali sehari."],
            "efek_samping": ["Mungkin menyebabkan rasa terbakar ringan pada mulut dan tenggorokan, reaksi alergi."],
            "indikasi": ["Sebagai antiseptik untuk mengatasi sakit tenggorokan, peradangan pada mulut dan tenggorokan"],
            "interaksi_obat": [],
            "jenis_obat": ["Obat kumur"],
            "kategori_obat": ["Antiseptik"],
            "kontraindikasi": ["Hipersensitivitas terhadap benzydamine atau komponen lain dalam sediaan."],
            "lama_penyimpanan": ["Lihat pada kemasan produk."],
            "mekanisme_kerja": ["Benzydamine memiliki efek analgetik dan antiinflamasi lokal."],
            "nama_dagang": ["Tantum Verde Gargle"],
            "nama_obat": "Tantum Verde Gargle 60 ml",
            "overdosis": ["Belum ada laporan terkait overdosis obat kumur ini."],
            "penjelasan_dosis": ["Berkumurlah selama 30-60 detik, kemudian buang larutan kumur."],
            "perhatian": ["Hanya untuk pemakaian luar. Jangan ditelan. Jauhkan dari jangkauan anak-anak."],
            "peringatan": ["Hentikan penggunaan dan konsultasi ke dokter jika terjadi reaksi alergi."],
            "persetujuan_regulator": ["BPOM"],
            "petunjuk_penyimpanan": ["Simpan pada suhu di bawah 30 derajat Celcius, terlindung dari cahaya matahari langsung."],
            "produsen": ["Sanofi"],
            "waktu_kerja": ["Efeknya akan terasa segera setelah berkumur."]
        },
        "name": "TANTUM VERDE GARGLE 60 ML",
        "satuan": "Botol"
    },
    {
        "_id": "01407c96-93aa-47d1-b1c1-330a2108d177",
        "code": "ALKS002955",
        "details": {
            "bahan_aktif": [],
            "dosis": [],
            "efek_samping": [],
            "indikasi": [],
            "interaksi_obat": [],
            "jenis_obat": [],
            "kategori_obat": [],
            "kontraindikasi": [],
            "lama_penyimpanan": [],
            "mekanisme_kerja": [],
            "nama_dagang": [],
            "nama_obat": "STETOSCOP",
            "overdosis": [],
            "penjelasan_dosis": [],
            "perhatian": [],
            "peringatan": [],
            "persetujuan_regulator": [],
            "petunjuk_penyimpanan": [],
            "produsen": [],
            "waktu_kerja": []
        },
        "name": "STETOSCOP",
        "satuan": "Piece"
    }
]

# Membuat DataFrame dari Data Dummy
df = pd.json_normalize(data_dummy)

smart_df = SmartDataframe(df, config={"llm": ollama_llm})

# Pertanyaan berbasis bahasa alami
question_1 = "Apa saja kategori obat dalam data ini?"
question_2 = "Tampilkan data untuk obat dengan nama 'Tantum Verde Gargle 60 ml'."
question_3 = "Berikan data semua item yang satuannya 'Piece'."

# Menjalankan analisis dengan PandasAI
result_1 = smart_df.chat(question_1)
result_2 = smart_df.chat(question_2)
result_3 = smart_df.chat(question_3)

# Menampilkan hasil
print("Pertanyaan 1:", question_1)
print("Jawaban 1:", result_1)
print('\n')

print("Pertanyaan 2:", question_2)
print("Jawaban 2:", result_2)
print('\n')

print("Pertanyaan 3:", question_3)
print("Jawaban 3:", result_3)
print('\n')


print("Pandas and PandasAI are working!")
