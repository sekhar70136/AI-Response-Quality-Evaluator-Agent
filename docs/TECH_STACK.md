Technology Stack
================

Introduction
------------

The AI Response Quality Evaluator combines a modern frontend, a Python backend, retrieval augmented generation techniques, and LLM based evaluation agents. The technologies chosen are lightweight, widely used, and well suited for building a modular and scalable system.

Technology Overview
-------------------

+----------------------+-------------------------------------------+
| Category             | Technology                                |
+======================+===========================================+
| Programming Language | Python                                    |
+----------------------+-------------------------------------------+
| Backend Framework    | FastAPI                                   |
+----------------------+-------------------------------------------+
| Frontend Framework   | React with Vite                           |
+----------------------+-------------------------------------------+
| Styling              | Tailwind CSS                              |
+----------------------+-------------------------------------------+
| LLM Provider         | Groq API                                  |
+----------------------+-------------------------------------------+
| LLM Model            | Llama 3.1 8B Instant                      |
+----------------------+-------------------------------------------+
| Embedding Model      | Sentence Transformers                     |
+----------------------+-------------------------------------------+
| Vector Database      | FAISS                                     |
+----------------------+-------------------------------------------+
| Reference Datasets   | TruthfulQA, SQuAD                         |
+----------------------+-------------------------------------------+
| HTTP Client          | Axios                                     |
+----------------------+-------------------------------------------+
| Visualization        | Chart.js                                  |
+----------------------+-------------------------------------------+
| PDF Export           | jsPDF and html2canvas                     |
+----------------------+-------------------------------------------+
| Version Control      | Git and GitHub                            |
+----------------------+-------------------------------------------+

Technology Details
------------------

Python
~~~~~~

Python is the main programming language used for the backend. It has a huge ecosystem for AI, machine learning, and natural language processing, which makes it a natural choice for this kind of project. Libraries for vector search, embeddings, and evaluation are all readily available in Python.

FastAPI
~~~~~~~

FastAPI is the backend framework. It is modern, fast, and generates automatic API documentation. It handles requests efficiently and works well with Pydantic for data validation.

React with Vite
~~~~~~~~~~~~~~~

React 18 is used to build the user interface. Vite provides a fast development experience and optimized production builds. The component based structure keeps the UI modular and easy to work with.

Tailwind CSS
~~~~~~~~~~~~

Tailwind CSS handles all the styling on the frontend. Its utility first approach makes it easy to build a consistent and responsive interface without writing a lot of custom CSS.

Groq API
~~~~~~~~

Groq provides the LLM inference for the evaluation agents. It offers fast inference speeds and has a free tier, which makes it great for development and testing. The system uses the OpenAI compatible Python SDK to talk to Groq's API.

Llama 3.1 8B Instant
~~~~~~~~~~~~~~~~~~~~

The default model used for evaluation is llama 3.1 8b instant. This model is configured through the GROQ_MODEL environment variable. It offers a good balance between speed and evaluation quality.

Sentence Transformers
~~~~~~~~~~~~~~~~~~~~~

Sentence Transformers are used to create vector embeddings from text. These embeddings capture the meaning of the text, which allows the system to find documents that are semantically similar instead of just matching keywords.

FAISS
~~~~~

FAISS, which stands for Facebook AI Similarity Search, is the vector database used to store and search document embeddings. It makes similarity search fast and efficient, so the system can retrieve relevant reference documents quickly.

TruthfulQA
~~~~~~~~~~

TruthfulQA is a benchmark dataset used to check the factual correctness of AI generated responses. It acts as a trusted source of reference information during evaluation.

SQuAD
~~~~~

SQuAD, or Stanford Question Answering Dataset, contains high quality question answer pairs that are widely used in NLP research. It provides reliable examples for testing and validating the evaluation pipeline.

Chart.js
~~~~~~~~

Chart.js is used in the frontend to display evaluation scores. It helps users quickly understand how the response performed across different quality dimensions.

jsPDF and html2canvas
~~~~~~~~~~~~~~~~~~~~~

These two libraries work together to let the frontend generate PDF reports of evaluation results. Users can download and share these reports easily.

Git and GitHub
~~~~~~~~~~~~~~

Git handles version control for the project, making it easy to track changes over time. GitHub is used as the central repository for the code, documentation, and collaboration.

Technology Stack Summary
------------------------

The chosen technologies support the full lifecycle of the application, from retrieving reference documents to evaluating responses and presenting results.

- Python provides the backend environment.
- FastAPI powers the backend services.
- React with Vite delivers a responsive user interface.
- Tailwind CSS handles styling.
- Groq API provides fast LLM inference for the evaluation agents.
- Sentence Transformers generate embeddings for document retrieval.
- FAISS stores and searches those embeddings efficiently.
- TruthfulQA and SQuAD supply trusted reference data.
- Chart.js visualizes the evaluation scores.
- jsPDF and html2canvas enable PDF report generation.
- Git and GitHub manage version control and collaboration.

Together, these technologies create a solid foundation for a modular, reliable, and scalable AI Response Quality Evaluator.
