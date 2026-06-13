# ATS Resume Scorer

A web app that scores how well a resume matches a job description and returns actionable feedback. Built with FastAPI + Streamlit, using spaCy and Sentence Transformers for NLP and the Groq API for LLM-generated suggestions.

## What it does

1. Upload a resume (PDF / DOC / DOCX) and paste a job description.
2. The backend parses the resume, extracts skills and experience, and compares them to the JD using semantic similarity.
3. You get an ATS score, a breakdown by category (formatting, keywords, content, skill validation, ATS compatibility), and LLM-written suggestions for what to improve.
4. Past analyses are saved to your account so you can revisit them.

## Tech stack

- **Frontend:** Streamlit
- **Backend:** FastAPI (Python)
- **NLP:** spaCy (`en_core_web_md`), Sentence Transformers (`all-MiniLM-L6-v2`)
- **LLM:** Azure AI Foundry (GPT-4o)
- **PDF report export:** WeasyPrint + Jinja2

## Project structure

```
ATS_SCORER/
├── backend/              FastAPI app, NLP services, API routes
├── frontend/             Streamlit app, views, components
├── jupyter notebooks/    Research and dataset prep
├── ml model/             Exported ML artifacts
├── requirements.txt      Combined backend + frontend dependencies
└── .env.example          Template for environment variables
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd ATS_SCORER
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install openai
python -m spacy download en_core_web_md
```

WeasyPrint needs system libraries on Linux:

```bash
# Fedora
sudo dnf install -y cairo pango gdk-pixbuf2 libffi

# Debian / Ubuntu
sudo apt install -y libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libffi-dev
```

### 3. Configure environment variables

Copy the template and fill in your keys:

```bash
cp .env.example .env
```


Required environment variables:


Azure AI Foundry: AZURE_ENDPOINT, AZURE_API_KEY, and ensure DEPLOYMENT_NAME is set to gpt-4o.
The Streamlit frontend also reads Supabase config from `frontend/.streamlit/secrets.toml`. Copy `secrets.toml.example` to `secrets.toml` and fill it in.

### 4. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now at `http://localhost:8000`.

### 5. Run the frontend

In a new terminal (with the venv activated):

```bash
streamlit run frontend/streamlit_app.py
```

The app opens at `http://localhost:8501`.


Notes:
 
Security: Never commit .env or secrets.toml files to GitHub — they contain sensitive API keys.

Azure AI: This project uses Azure AI Foundry for secure, scalable LLM inference. Ensure your environment variables are configured to connect to your Azure deployment correctly.