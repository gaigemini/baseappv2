from fastapi import APIRouter
import requests, json
from pymongo.errors import PyMongoError, DuplicateKeyError

from baseapp.model.common import ApiResponse

from baseapp.config import setting, mongodb
config = setting.get_settings()

import logging, httpx
logger = logging.getLogger()

router = APIRouter(prefix="/v1/ai", tags=["AI"])

# URL API Ollama
OLLAMA_MODELS_URL = "http://localhost:11435/v1/models"
OLLAMA_COMPLETIONS_URL = "http://localhost:11435/v1/completions"

def list_ollama_models():
    try:
        response = requests.get(OLLAMA_MODELS_URL)
        response.raise_for_status()
        models = response.json()
        logger.info("Daftar Model yang Tersedia di Ollama:")
        for model in models.get('data', []):
            logger.info(f"- ID: {model['id']}, Diciptakan pada: {model['created']}, Dimiliki oleh: {model['owned_by']}")
    except requests.RequestException as e:
        raise ValueError(f"Error saat mengambil daftar model: {e}")

def generate_prompt(collection_name, fields, user_query):
    field_descriptions = "\n".join([f"- `{field}` ({dtype}): {desc}" for field, dtype, desc in fields])
    return (
        # f"You are an expert in MongoDB queries. I will provide you with a user question and the structure of a MongoDB collection. "
        # f"Respond with a valid MongoDB agregate pipiline query in JSON format, and explain the query briefly.\n\n"
        # f"Collection name: `{collection_name}`\n"
        # f"Fields:\n{field_descriptions}\n\n"
        # f"User Query: \"{user_query}\"\n\n"
        # f"MongoDB Query:"

        f"You are an expert in MongoDB queries. I will provide you with a user question and the structure of a MongoDB collection. "
        f"Your task is to respond with a valid MongoDB aggregate pipeline query in JSON format. "
        f"Ensure the JSON is well-formed and explain the query briefly.\n\n"
        f"Collection name: `{collection_name}`\n"
        f"Fields:\n{field_descriptions}\n\n"
        f"User Query: \"{user_query}\"\n\n"
        f"Expected Output:\n"
        f"1. MongoDB Aggregate Pipeline Query (in JSON format).\n"
        f"2. Brief explanation of the query.\n\n"
        f"Example Response Format:\n"
        f"```json\n"
        f"{{\n"
        f"  \"pipeline\": [\n"
        f"    {{ \"$match\": {{ \"field\": \"value\" }} }},\n"
        f"    {{ \"$group\": {{ \"_id\": \"$field\", \"count\": {{ \"$sum\": 1 }} }} }}\n"
        f"  ]\n"
        f"}}\n"
        f"```\n"
        f"Explanation:\n- Explain each stage briefly.\n\n"
        f"Now, please respond based on the following user query and collection structure:\n\n"
        f"User Query: \"{user_query}\"\n\n"
        f"MongoDB Query:"
    )

def query_ollama(model, prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt
    }

    try:
        response = requests.post(OLLAMA_COMPLETIONS_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.RequestException as e:
        print(f"Error menghubungkan ke Ollama API: {e}")
        return None

# Fungsi untuk mengekstrak JSON query dan explanation dari respons API
def extract_query_and_explanation(api_response):
    # Ambil teks dari "choices"
    response_text = api_response["choices"][0]["text"]

    # Ekstrak bagian JSON query
    json_query_start = response_text.find("```json") + len("```json")
    json_query_end = response_text.find("```", json_query_start)
    json_query_str = response_text[json_query_start:json_query_end].strip()

    # Ekstrak bagian explanation
    explanation_start = response_text.find("### Explanation:") + len("### Explanation:")
    explanation = response_text[explanation_start:].strip()

    # Konversi JSON query menjadi dictionary Python
    json_query = json.loads(json_query_str)

    return json_query, explanation

@router.get("/test", response_model=ApiResponse)
async def test_ai() -> ApiResponse:
    list_ollama_models()
    
    # Pilih model yang akan digunakan
    selected_model = "qwen2.5:latest"  # Ganti dengan model yang Anda pilih
    
    # Contoh penggunaan
    collection_name = "obat"
    # fields = [
    #     ("name", "string", "The name of the user."),
    #     ("age", "number", "The age of the user."),
    #     ("email", "string", "The email address of the user."),
    #     ("created_at", "date", "The date the user was created."),
    #     ("is_active", "boolean", "Indicates if the user is active.")
    # ]
    fields = [
        ("_id", "string", "Unique identifier for the record."),
        ("code", "string", "The code of the medicine."),
        ("details.bahan_aktif", "array", "The active ingredients of the medicine."),
        ("details.dosis", "array", "The dosage instructions."),
        ("details.efek_samping", "array", "Possible side effects of the medicine."),
        ("details.indikasi", "array", "Indications or purposes of the medicine."),
        ("details.interaksi_obat", "array", "Interactions with other medicines."),
        ("details.jenis_obat", "array", "The type of the medicine."),
        ("details.kategori_obat", "array", "The category of the medicine."),
        ("details.kontraindikasi", "array", "Contraindications of the medicine."),
        ("details.lama_penyimpanan", "array", "The storage duration of the medicine."),
        ("details.mekanisme_kerja", "array", "Mechanism of action of the medicine."),
        ("details.nama_dagang", "array", "The trade names of the medicine."),
        ("details.nama_obat", "string", "The full name of the medicine."),
        ("details.overdosis", "array", "Overdose information."),
        ("details.penjelasan_dosis", "array", "Detailed dosage instructions."),
        ("details.perhatian", "array", "Precautions when using the medicine."),
        ("details.peringatan", "array", "Warnings associated with the medicine."),
        ("details.persetujuan_regulator", "array", "Regulatory approvals for the medicine."),
        ("details.petunjuk_penyimpanan", "array", "Storage instructions for the medicine."),
        ("details.produsen", "array", "The manufacturer of the medicine."),
        ("details.waktu_kerja", "array", "The time it takes for the medicine to work."),
        ("name", "string", "The name of the medicine."),
        ("satuan", "string", "The unit of the medicine (e.g., bottle).")
    ]
    user_query = "Find all medicines containing 'Paracetamol' as an active ingredient and sort them by their name in ascending order"
    # user_query = "Find all medicines categorized as 'Antiseptik' but exclude those with 'Hipersensitivitas' in their contraindications. Sort the results by their code in descending order."
    # user_query = "Find all medicines indicated for 'fever' with a dosage containing '1 tablet every 8 hours'. Sort the results by creation date in descending order."
    # user_query = "Find all active users above 25 years old and sort them by their creation date in descending order."
    
    prompt = generate_prompt(collection_name, fields, user_query)

    # Eksekusi perintah
    result = query_ollama(selected_model,prompt)

    # Panggil fungsi untuk memproses respons
    json_query, explanation = extract_query_and_explanation(result)

    # test run mongodb
    client = mongodb.MongoConn(host="202.149.86.226",port=27017,database="obat",username="admin",password="e7ax7vW2K85L")
    with client as mongo:
        collection = mongo._db[collection_name]
        try:
            # Execute aggregation pipeline
            cursor = collection.aggregate(json_query["pipeline"])
            res_data = list(cursor)
        except PyMongoError as pme:
            raise ValueError("Database error while retrieve document") from pme
        except Exception as e:
            raise

    return ApiResponse(status=0, message=explanation, data=res_data)
    
    

    
