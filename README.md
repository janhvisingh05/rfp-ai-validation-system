# rfp-ai-validation-system

# AI-Powered RFP Qualification Criteria Validation System

An intelligent system that automates the validation and scoring of RFP (Request for Proposal) submissions using Large Language Models (LLMs) and a multi-agent architecture.

This project simulates real-world procurement workflows by validating bidder documents against qualification criteria and generating pass/fail decisions with automated scoring.

---

## Overview

This application enables users to upload RFP-related documents and automatically evaluates them against predefined qualification criteria.

It combines:

* Document parsing (DOCX → text)
* Multi-agent LLM reasoning (AutoGen)
* Rule-based scoring logic

The system reduces manual effort in vendor evaluation and improves consistency and transparency.

---

## Key Features

* 📄 Upload multiple RFP documents (Annexures, Certificates, Letters)
* 🤖 AI-based validation using LLM agents
* 🧠 Multi-agent architecture (Orchestrator + Validation Agent)
* 📊 Automatic scoring of qualification criteria
* 📈 Tabular results + validation logs
* ⚡ Interactive Streamlit UI

---

## Tech Stack

* **Frontend/UI:** Streamlit
* **Backend:** Python
* **AI Framework:** AutoGen
* **LLM Integration:** OpenAI API
* **Data Processing:** Pandas
* **Document Parsing:** Mammoth
* **Database Logic:** SQLite (in-memory)
* **Environment Config:** python-dotenv

---

## Project Structure

```
rfp-ai-validation/
│
├── main_app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   ├── import_df.xlsx
│   └── model_rfpscoring.xlsx
├── documents/
│   ├── ANNEXURE_2.docx
│   ├── ANNEXURE_5.docx
│   ├── Company_Credentials_Document.docx
│   ├── confirmation_letter.docx
│   ├── Pre_Contract_Integrity_Pact.docx
│   ├── self_declaration.docx
│   └── undertaking_letter.docx
```

---

## Installation & Setup (For New Users)

### 1. Clone the repository

```
git clone https://github.com/YOUR_USERNAME/rfp-ai-validation-system.git
cd rfp-ai-validation-system
```

### 2. Create virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Setup environment variables

Create a `.env` file in root directory:

```
OPENAI_API_KEY=your_api_key_here
MODEL=gpt-4
CRITIC_MODEL=gpt-4
human_input_mode=NEVER
orchestrator_name=orchestrator
```

---

## Running the Application

```
streamlit run main_app.py
```

---

## How It Works

### 1. Input Criteria

* Reads qualification criteria from Excel dataset
* Example includes pre-qualification conditions used in RFPs

### 2. Document Processing

* Uploaded DOCX files are converted into clean text using Mammoth

### 3. AI Validation

* Multi-agent system evaluates:

  * Whether criteria are satisfied
  * Generates reasoning
  * Outputs structured result:

```
{"Validation Result": "Pass"}
```

### 4. Scoring System

* Pass → Allocated points
* Fail → 0 points
* Final score calculated using SQLite queries

### 5. Output

* Validation logs
* Criteria-wise results table
* Total score summary

---

## Environment Variables Guide

| Variable          | Description                     |
| ----------------- | ------------------------------- |
| OPENAI_API_KEY    | Your OpenAI API key             |
| MODEL             | Primary LLM model (e.g., gpt-4) |
| CRITIC_MODEL      | Secondary model for evaluation  |
| human_input_mode  | Agent interaction mode          |
| orchestrator_name | Name of orchestrator agent      |

---

## Required Libraries

Minimal required dependencies:

```
streamlit
pandas
numpy
openpyxl
python-dotenv
mammoth
autogen
openai
```

---

## ⚠️ Important Code Fixes (Before Upload / Use)

### 1. ❌ Hardcoded Local Path (BREAKS PROJECT)

Current:

```
UPLOAD_FOLDER = "/Users/janhvi/Desktop/..."
```

✅ Fix:

```
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

---

### 2. ❌ Windows-specific file path

Current:

```
C:/Users/HP/Documents/...
```

✅ Fix:

```
import_df.xlsx  (place inside /data folder)
```

Update code:

```
pd.read_excel("data/import_df.xlsx")
```

---

### 3. ❌ Missing `.env` handling safety

Add fallback:

```
os.getenv("OPENAI_API_KEY")
```

---

### 4. ❌ File dependency assumptions

Ensure:

* All required documents exist OR
* Add validation checks before processing

---

## Known Limitations

* Requires structured Excel input format
* LLM responses may vary (non-deterministic)
* Requires OpenAI API access (paid usage)
* No authentication or user management
* Local file storage (not cloud-ready)
* Hard dependency on document formats (DOCX only)
* No error handling for malformed inputs
* UI does not support dynamic configuration of criteria

---

## Future Improvements

* Dynamic criteria configuration UI
* Machine learning-based scoring
* Document classification and tagging
* Cloud deployment (AWS / Azure / GCP)
* Multi-user authentication system
* API-based architecture

---

## Use Cases

* Vendor evaluation in procurement
* Government tender validation
* Consulting bid analysis
* Automated compliance checking

---

## Author

**Janhvi Singh**

---

## License

This project is intended for educational and portfolio use.
