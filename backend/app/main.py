from fastapi import FastAPI

app = FastAPI(
    title="Career Forge AI",
    version="1.0.0",
    description="AI Job Search Assistant"
)


@app.get("/")
def root():
    return {
        "message": "Career Forge AI API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
