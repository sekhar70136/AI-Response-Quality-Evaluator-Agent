# AI Response Quality Evaluator Agent

An intelligent multi-agent system for evaluating the quality of Large Language Model (LLM) responses using Retrieval-Augmented Generation (RAG), specialized evaluation agents, batch evaluation, analytics, and automated reporting.

![Python](https://img.shields.io/badge/Python-FastAPI-blue) ![React](https://img.shields.io/badge/React-Vite-61DAFB) ![Groq](https://img.shields.io/badge/LLM-Groq-orange) ![RAG](https://img.shields.io/badge/RAG-FAISS-green) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Project Overview

Large Language Models are capable of generating fluent, context-aware responses — but these responses can still suffer from problems such as:

- Hallucinated information
- Factual inaccuracies
- Irrelevant content
- Unsupported claims
- Incomplete answers

Manually evaluating LLM responses for these issues is subjective, slow, and hard to scale.

The **AI Response Quality Evaluator Agent** solves this by providing an automated, multi-dimensional evaluation framework. Rather than relying on a single evaluator, the system uses a **multi-agent architecture**, where each agent independently judges one specific aspect of response quality. The evaluation is grounded using **Retrieval-Augmented Generation (RAG)**, so agents compare responses against relevant reference knowledge before scoring them — reducing reliance on the LLM's own unverified judgment.

---

## ✨ Key Features

- 🤖 **Multi-Agent Evaluation** — Relevance, Accuracy, Hallucination, and Completeness are each judged by a dedicated agent.
- 📚 **RAG-Based Evaluation** — Retrieves supporting evidence from a semantic knowledge base using Sentence-Transformers and FAISS.
- 🎯 **Evidence-Aware Scoring** — Accuracy and Hallucination checks are marked unverifiable (N/A) when grounding evidence isn't available, instead of guessing.
- 📦 **Batch Evaluation** — Evaluate many question-response pairs at once via CSV upload.
- 📊 **Evaluation Dashboard** — Score breakdowns, dimension-wise analytics, verdict distribution, and quality trends, visualized with Chart.js.
- 📄 **PDF Report Export** — Generate downloadable evaluation reports directly from the dashboard using jsPDF and html2canvas.

---

## 🤖 Multi-Agent Evaluation

| Agent | Responsibility |
|---|---|
| **Relevance Judge** | Checks whether the response directly addresses the user's question |
| **Accuracy Judge** | Verifies factual correctness against retrieved or reference evidence |
| **Hallucination Judge** | Flags claims not supported by the available evidence |
| **Completeness Judge** | Checks whether all parts of the question were addressed |
| **Verdict Agent** | Aggregates all four scores into a final, weighted verdict |

### Relevance Judge
Evaluates how directly the AI-generated response answers the user's question, producing a relevance score with supporting reasoning.

### Accuracy Judge
Checks factual correctness using the optional reference answer and any relevant evidence retrieved through the RAG pipeline. If no reliable grounding evidence is available, the dimension is returned as **unverifiable (N/A)** rather than being scored blindly.

### Hallucination Judge
Cross-references each claim in the response against retrieved source content and flags statements that are unsupported or contradicted. Like the Accuracy Judge, this falls back to N/A when there isn't enough grounding evidence to check against.

### Completeness Judge
Determines whether the response covers every aspect of the question that was asked, and calls out specific omissions.

### Verdict Agent
Combines all four dimension scores using a **weighted scoring model** to produce:
- Overall Score
- Final Verdict — Pass / Needs Improvement / Fail
- Consolidated Evaluation Summary

This design keeps each quality dimension independently explainable while still producing one clear, unified assessment.

---

## 📚 Retrieval-Augmented Evaluation

```
Knowledge Base
      ↓
Document Chunking + Embeddings (Sentence-Transformers)
      ↓
FAISS Vector Index
      ↓
Question Embedding
      ↓
Top-K Semantic Retrieval
      ↓
Similarity Threshold Filtering
      ↓
Relevant Evidence
      ↓
Accuracy & Hallucination Evaluation
```

The knowledge base is seeded using public QA benchmark datasets (**TruthfulQA** and **SQuAD**), chunked and embedded to support grounded, evidence-based judging rather than evaluation based purely on the LLM's internal knowledge.

---

## 📁 Batch Evaluation

The Batch Evaluation module lets users upload a CSV of multiple question-response pairs and evaluate them all in one pass.

**Supported CSV columns:**
- `question` — required
- `response` — required
- `reference` — optional

Each row is run through the full multi-agent pipeline, and results are aggregated into:
- Total row count
- Successful / partial / failed evaluations
- Average quality score
- Verdict distribution across the batch
- Individual per-row results

Only fully successful rows are included in the aggregate score and verdict statistics, so incomplete evaluations don't skew the numbers.

---

## 📊 Evaluation Dashboard

Built with **React**, **Chart.js**, and **Tailwind CSS**, the dashboard visualizes:

- Average score per dimension (Relevance, Accuracy, Hallucination, Completeness)
- Best and weakest performing dimensions
- Hallucination frequency across evaluations
- Verdict distribution (Pass / Needs Improvement / Fail)
- Overall quality trend across submissions

## 📄 PDF Report Export

Evaluation results — single or batch — can be exported as a downloadable PDF report directly from the dashboard, generated client-side using **jsPDF** and **html2canvas**.

---

## 🏗 System Architecture

The application is organized into four logical layers:

| Layer | Responsibility |
|---|---|
| **Presentation Layer** | React + Vite frontend for submitting responses and viewing results |
| **Application Layer** | FastAPI backend coordinating the evaluation workflow |
| **Intelligence Layer** | RAG retrieval, Groq LLM calls, and the specialized evaluation agents |
| **Data Layer** | Knowledge base, benchmark datasets, and stored evaluation data |

### Response Evaluation Workflow

```
                    User Input
                        │
                        ▼
              Evaluation Input Module
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  Single Evaluation              Batch Evaluation
         │                             │
         └──────────────┬──────────────┘
                         ▼
                   RAG Retrieval
                         │
                         ▼
              Reference Knowledge Base
                         │
                         ▼
              Multi-Agent Evaluation
                         │
   ┌────────────┬────────────┬────────────┐
   ▼            ▼            ▼            ▼
Relevance    Accuracy   Hallucination  Completeness
  Judge        Judge        Judge          Judge
   │            │            │            │
   └────────────┴──────┬─────┴────────────┘
                        ▼
                  Verdict Agent
                        │
                        ▼
              Weighted Quality Score
                        │
                        ▼
           Pass / Needs Improvement / Fail
                        │
                        ▼
                Evaluation Dashboard
```

---

## 🧩 Technology Stack

**Frontend**
| Component | Technology |
|---|---|
| Framework | React 18.3 + Vite 5.4 |
| Styling | Tailwind CSS 3.4 |
| HTTP Client | Axios |
| Charts | Chart.js 4.5 |
| PDF Export | jsPDF + html2canvas |

**Backend**
| Component | Technology |
|---|---|
| API Server | FastAPI 0.110 + Uvicorn |
| Data Validation | Pydantic |
| LLM Integration | Groq (via OpenAI-compatible SDK) |
| Embeddings | Sentence-Transformers |
| Vector Search | FAISS |
| Config | python-dotenv |

---

## 📂 Repository Structure

```
AI-Response-Quality-Evaluator-Agent/
│
├── backend/
│   ├── agents/
│   │   ├── relevance_judge.py
│   │   ├── accuracy_judge.py
│   │   ├── hallucination_judge.py
│   │   ├── completeness_judge.py
│   │   ├── verdict_agent.py
│   │   └── prompts/
│   │       ├── relevance_prompt.py
│   │       ├── accuracy_prompt.py
│   │       ├── hallucination_prompt.py
│   │       └── completeness_prompt.py
│   │
│   ├── rag/
│   │   ├── build_index.py
│   │   ├── retriever.py
│   │   ├── dataset_loader.py
│   │   ├── faiss_index.bin
│   │   └── metadata.json
│   │
│   ├── services/
│   │   └── evaluation_service.py
│   │
│   ├── controller.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
│
├── datasets/
│   ├── squad.csv
│   └── truthfulqa.csv
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DashboardCharts.jsx
│   │   │   ├── BatchEvaluation.jsx
│   │   │   ├── BatchCharts.jsx
│   │   │   ├── ScoreCard.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── Loader.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── .env
├── .gitignore
├── start_backend.bat
└── README.md
```

---

## ⚙️ Installation

### Clone the repository
```bash
git clone <your-repository-url>
cd AI-Response-Quality-Evaluator-Agent
```

### Backend setup
```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:
```
GROQ_API_KEY=your_groq_api_key
```

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

### Frontend setup
```bash
cd frontend
npm install
npm run dev
```

By default, the frontend runs at `http://localhost:5173` and communicates with the FastAPI backend.

---

## 💡 Using the Application

1. Enter a **User Question**.
2. Paste the **AI Generated Response** to be evaluated.
3. *(Optional)* Provide a **Reference Answer** for stricter grounding.
4. Click **Evaluate**.

The system returns:
- Relevance score and reasoning
- Accuracy score with supporting evidence
- Hallucination findings (or N/A if unverifiable)
- Completeness score and any omissions
- Overall weighted score and final verdict

For bulk evaluation, switch to the **Batch Evaluation** tab and upload a CSV file containing `question`, `response`, and optionally `reference` columns.

---

## 🔮 Future Work

- REST API expansion for third-party integration
- Docker-based deployment
- Database-backed evaluation history
- Additional evaluation dimensions (Safety, Bias, Clarity, Style)
- Model comparison across multiple LLM providers

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🙏 Acknowledgements

This project builds on ideas, tools, and datasets from the open-source community, including Groq, FAISS, Sentence-Transformers, TruthfulQA, SQuAD, and Hugging Face.

---

## 👨‍💻 Author

**Soma Sekhar**
B.Tech – Computer Science (Artificial Intelligence & Data Science)
Vishnu Institute of Technology
Infosys Springboard Internship Project – 2026
