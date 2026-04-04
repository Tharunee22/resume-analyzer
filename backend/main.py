from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from typing import List
from fastapi.responses import FileResponse
import shutil
import os
import fitz
import docx
import re
import string
import uuid
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- FOLDERS --------
UPLOAD_FOLDER = "uploads"
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)

# -------- LOAD MODEL ONCE --------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -------- TEXT EXTRACTION --------
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return " ".join([page.get_text() for page in doc])

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# -------- PREPROCESSING --------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

# -------- EMBEDDING --------
def get_embeddings(text_list):
    return model.encode(text_list)

# -------- CLEAR OLD FILES --------
def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        return
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# -------- ROOT --------
@app.get("/")
def home():
    return {"message": "Resume Analyzer API is running"}

# -------- ANALYZE API --------
@app.post("/analyze/")
async def analyze(
    jd: UploadFile = File(...),
    resumes: List[UploadFile] = File(...)
):

    # Clear old resumes
    clear_folder(RESUME_FOLDER)

    # -------- Save JD --------
    jd_filename = str(uuid.uuid4()) + "_" + jd.filename
    jd_path = os.path.join(UPLOAD_FOLDER, jd_filename)

    with open(jd_path, "wb") as buffer:
        shutil.copyfileobj(jd.file, buffer)

    # -------- Save Resumes --------
    saved_files = []

    for resume in resumes:
        unique_name = str(uuid.uuid4()) + "_" + resume.filename
        path = os.path.join(RESUME_FOLDER, unique_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        saved_files.append((resume.filename, path))

    # -------- Process JD --------
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = preprocess_text(f.read())

    jd_embedding = get_embeddings([jd_text])[0]

    results = []

    # -------- Process Resumes --------
    for original_name, path in saved_files:

        if path.endswith(".pdf"):
            text = extract_text_from_pdf(path)
        elif path.endswith(".docx"):
            text = extract_text_from_docx(path)
        else:
            continue

        text = preprocess_text(text)

        resume_embedding = get_embeddings([text])[0]

        score = cosine_similarity([jd_embedding], [resume_embedding])[0][0]

        results.append({
            "Resume File": original_name,
            "Similarity Score": float(score)
        })

    # -------- Sort Results --------
    results = sorted(results, key=lambda x: x["Similarity Score"], reverse=True)

    # -------- Save CSV --------
    csv_path = os.path.join(UPLOAD_FOLDER, "results.csv")

    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False)

    return results

# -------- DOWNLOAD CSV API --------
@app.get("/download-csv/")
def download_csv():
    file_path = os.path.join(UPLOAD_FOLDER, "results.csv")

    return FileResponse(
        path=file_path,
        filename="resume_scores.csv",
        media_type="text/csv"
    )