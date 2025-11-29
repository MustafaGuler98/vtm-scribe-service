import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.models import CharacterRequest
from app.services.pdf_service import PdfService

app = FastAPI(
    title="Elysium PDF Service",
    description="Microservice for VtM Character Generator: Elysium.",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "fillable_v20.pdf")

@app.get("/")
def read_root():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "active", "service": "Elysium PDF Service"}

@app.post("/generate-pdf", response_class=StreamingResponse)
async def generate_pdf(character: CharacterRequest):
    """
    Generates a filled PDF character sheet in-memory and streams it back to the client.
    
    - **character**: The JSON payload containing character details.
    - **Returns**: A PDF file stream (application/pdf).
    """
    try:
        pdf_service = PdfService(TEMPLATE_PATH)
        
        # Convert Pydantic model to dict for processing
        char_data = character.model_dump()
        pdf_stream = pdf_service.generate_character_stream(char_data)
        pdf_size = pdf_stream.getbuffer().nbytes

        # Create a safe filename
        safe_name = character.name.replace(" ", "_") if character.name else "Character"
        filename = f"{safe_name}_Sheet.pdf"

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(pdf_size)
        }
        
        # Return the stream directly. No disk storage used.
        return StreamingResponse(
            pdf_stream, 
            media_type="application/pdf",
            headers=headers
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Configuration Error: PDF Template not found. {str(e)}")
        
    except Exception as e:
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail=f"The scribe is currently overwhelmed. Please try again in a moment. (Error: {str(e)})"
        )