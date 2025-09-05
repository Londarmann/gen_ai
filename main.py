import os
from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import openai
from dotenv import load_dotenv
import tempfile

load_dotenv()

app = FastAPI(
    title="app",
    description="API for processing voice input and generating responses using AI",
)


openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Models
class VoiceResponse(BaseModel):
    text: str
    response: str
    model: str = "gpt-3.5-turbo"

async def transcribe_audio(audio_file_path: str) -> str:
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {str(e)}"
        )

async def generate_response(text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds to voice messages."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

@app.post("/process-voice/", response_model=VoiceResponse)
async def process_voice(audio_file: UploadFile):
    allowed_content_types = [
        'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/mpeg',
        'audio/mpga', 'audio/m4a', 'audio/wav', 'audio/webm'
    ]
    
    if audio_file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported types: {', '.join(allowed_content_types)}"
        )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        try:
            contents = await audio_file.read()
            temp_audio.write(contents)
            temp_audio_path = temp_audio.name
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing audio file: {str(e)}"
            )
    
    try:
        
        transcribed_text = await transcribe_audio(temp_audio_path)
        

        ai_response = await generate_response(transcribed_text)
        
        return VoiceResponse(
            text=transcribed_text,
            response=ai_response,
            model="gpt-3.5-turbo"
        )
    finally:

        try:
            os.unlink(temp_audio_path)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)