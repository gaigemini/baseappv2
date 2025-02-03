import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM

# llm_model = "qwen2.5:latest"
llm_model = "deepseek-r1:32b"
ollama_llm = LocalLLM(api_base="http://202.149.64.34:11434/v1", model=llm_model)

# Data Dummy (Array)
data_dummy = [
    {"name": "Alice", "age": 25, "income": 50000},
    {"name": "Bob", "age": 32, "income": 60000},
    {"name": "Charlie", "age": 29, "income": 55000},
    {"name": "Diana", "age": 35, "income": 70000},
    {"name": "Edward", "age": 40, "income": 80000},
    {"name": "Aldian", "age": 31, "income": 100000}
]

# Membuat DataFrame dari Data Dummy
df = pd.DataFrame(data_dummy)

smart_df = SmartDataframe(df, config={"llm": ollama_llm})
# limited_df = smart_df.head(10)

# Pertanyaan berbasis bahasa alami
question_1 = "Siapa yang memiliki penghasilan tertinggi?"
question_2 = "Berapa rata-rata usia di dataset ini?"
question_3 = "Tampilkan orang yang usianya lebih dari 30 tahun."

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
