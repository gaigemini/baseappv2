from fastapi import APIRouter
import requests, json, re
from pymongo import MongoClient

from baseapp.model.common import ApiResponse

from baseapp.config import setting
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
        f"You are an expert in MongoDB queries. I will provide you with a user question and the structure of a MongoDB collection. "
        f"Respond with a valid MongoDB query in JSON format, and explain the query briefly.\n\n"
        f"Collection name: `{collection_name}`\n"
        f"Fields:\n{field_descriptions}\n\n"
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
    collection_name = "users"
    fields = [
        ("name", "string", "The name of the user."),
        ("age", "number", "The age of the user."),
        ("email", "string", "The email address of the user."),
        ("created_at", "date", "The date the user was created."),
        ("is_active", "boolean", "Indicates if the user is active.")
    ]
    user_query = "Find all active users above 25 years old and sort them by their creation date in descending order."
    
    prompt = generate_prompt(collection_name, fields, user_query)

    # Eksekusi perintah
    result = query_ollama(selected_model,prompt)

    # Panggil fungsi untuk memproses respons
    json_query, explanation = extract_query_and_explanation(result)

    return ApiResponse(status=0, message=explanation, data=json_query)
    
    

    
