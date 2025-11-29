from fastapi import FastAPI

app = FastAPI(
    title="Elysium PDF Service",
    description="Pdf microservice for vtm character generator: Elysium.",
    version="1.0.0"
)

# For testing.
@app.get("/")
def read_root():
    return {"status": "active", "message": "Elysium PDF Service is running..."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}