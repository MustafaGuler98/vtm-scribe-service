import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import CharacterRequest
from app.services.pdf_service import PdfService
import time

app = FastAPI(
    title="Elysium PDF Service",
    description="Microservice for VtM Character Generator: Elysium.",
    version="1.0.0"
)

# --- CORS CONFIGURATION ---
# This is crucial for allowing the browser to communicate directly with this service.
# We must explicitly list all domains that are allowed to make requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://elysium.mustafaguler.me", # Production domain
        "http://localhost:5000",           # Local development
        "http://127.0.0.1:5000"            # Local development (alternative)
    ],
    allow_credentials=True,
  
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "fillable_v20.pdf")

@app.get("/")
def read_root():
    """
    Health check endpoint.
    """
    return {"status": "active", "service": "Elysium PDF Service"}

@app.post("/generate-pdf", response_class=StreamingResponse)
async def generate_pdf(character: CharacterRequest):
    """
    Generates a filled PDF and streams it directly to the client.
    Using chunked transfer encoding to improve Time-To-First-Byte (TTFB).
    """
    start_time = time.time()
    try:
        print(f"[LOG] Generation started for character: {character.name}")
        
        pdf_service = PdfService(TEMPLATE_PATH)
        char_data = character.model_dump()
        
        pdf_stream = pdf_service.generate_character_stream(char_data)
        
        # This prevents the server from needing to buffer the entire file before sending response headers
        def iterfile():
            pdf_stream.seek(0)
            while True:
                chunk = pdf_stream.read(4096)  # Read in 4KB chunks
                if not chunk:
                    break
                yield chunk

        # Safe filename creation
        safe_name = character.name.replace(" ", "_") if character.name else "Character"
        filename = f"{safe_name}_Sheet.pdf"

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Process-Time": str(time.time() - start_time) # Custom header for debugging latency
        }
        
        print(f"[LOG] Stream ready in {time.time() - start_time:.4f}s. Sending response...")

        return StreamingResponse(
            iterfile(), 
            media_type="application/pdf",
            headers=headers
        )

    except FileNotFoundError as e:
        print(f"[ERROR] Template missing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration Error: PDF Template not found.")
        
    except Exception as e:
        print(f"[ERROR] Critical failure: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"The scribe is currently overwhelmed. Error: {str(e)}"
        )