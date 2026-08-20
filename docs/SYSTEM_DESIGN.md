System Design
=============

Introduction
------------

This document describes the system architecture and design of the AI Response Quality Evaluator. The system is built with a React frontend, a FastAPI backend, and a RAG powered evaluation pipeline that uses multiple specialized agents to judge AI generated responses.

System Architecture
-------------------

The application is split into two main parts: the frontend and the backend.

Frontend Layer
~~~~~~~~~~~~~~

The frontend is built with React and Vite, styled using Tailwind CSS. It provides the user interface where users can enter a question and an AI generated response. After the evaluation is complete, the frontend displays the scores, shows charts for visualization, and lets users export the results as a PDF.

Backend Layer
~~~~~~~~~~~~~

The backend is built with FastAPI and runs on Uvicorn. It handles the core logic of the application, including receiving user input, retrieving reference documents, running the evaluation agents, and returning the final report.

RAG Retriever
~~~~~~~~~~~~~

The retriever uses Sentence Transformers to convert text into vector embeddings. These embeddings are stored in a FAISS vector database. When a question comes in, the system searches the vector store to find the most relevant reference documents from the TruthfulQA and SQuAD datasets.

Evaluation Engine
~~~~~~~~~~~~~~~~

The evaluation engine coordinates four specialized agents. Each agent focuses on one aspect of quality: relevance, accuracy, hallucination, and completeness. Every agent uses the Groq API, specifically the Llama 3.1 8B Instant model, to judge the response and provide a score along with feedback.

Verdict Agent
~~~~~~~~~~~~~

After all four agents finish their evaluation, the Verdict Agent collects the individual scores, calculates an overall quality score, and writes the final evaluation summary.

LLM Layer
~~~~~~~~~

The system uses Groq as the LLM provider. The OpenAI Python SDK is used to call Groq's API since Groq offers an OpenAI compatible endpoint. The default model is llama 3.1 8b instant, but this can be changed through the GROQ_MODEL environment variable.

How Data Flows Through the System
---------------------------------

1. The user enters a question and an AI generated response in the React frontend.
2. The frontend sends this data to the FastAPI backend through an API call.
3. The backend uses the RAG retriever to search the FAISS vector store and pull out relevant reference documents.
4. The evaluation engine sends the question, response, and retrieved context to four agents: Relevance, Accuracy, Hallucination, and Completeness.
5. Each agent calls the Groq API to get a score and feedback for its specific check.
6. The Verdict Agent gathers all four scores, computes the overall quality score, and prepares the final report.
7. The backend sends the complete evaluation report back to the frontend.
8. The frontend shows the scores, draws charts, and allows the user to download a PDF report.

API Endpoints
-------------

The backend exposes the following endpoints:

POST /api/evaluate
    Accepts a user question and an AI generated response, runs the full evaluation pipeline, and returns the evaluation report.

GET /api/health
    A simple health check endpoint to confirm the backend is running.

Environment Variables
---------------------

The backend requires the following environment variables:

GROQ_API_KEY
    The API key for accessing the Groq service. This must be obtained from the Groq console.

GROQ_MODEL
    The model name to use for evaluation. The default value is llama-3.1-8b-instant.

How to Run the Project
----------------------

Backend
~~~~~~~

To start the backend server, run:

    uvicorn main:app --reload

Make sure the virtual environment is activated and all dependencies from requirements.txt are installed before running this command.

Frontend
~~~~~~~~

To start the frontend development server, run:

    npm run dev

This starts the Vite dev server and opens the application in the browser.

Production Build
~~~~~~~~~~~~~~~~

For production, build the frontend using:

    npm run build

The built frontend can then be served through FastAPI or any static file server.
