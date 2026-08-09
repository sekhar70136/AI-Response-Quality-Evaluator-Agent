from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller import router as evaluation_router

app = FastAPI(title="AI Response Quality Evaluator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluation_router)


@app.get("/")
def health_check():
    """Simple health endpoint for verifying the API is running."""
    return {"status": "ok", "message": "AI Response Quality Evaluator API is running"}
