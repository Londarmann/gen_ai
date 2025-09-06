# Voice Processing API Architecture

## System Architecture

```mermaid
flowchart TD
    A[Client] -->|1. Upload Audio File| B[FastAPI Server]
    B -->|2. Save Temporary File| C[File System]
    B -->|3. Send Text| D[Google Gemini API]
    D -->|4. Return AI Response| B
    B -->|5. Return Response| A
    B -->|6. Clean Up| C

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#f96,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as FastAPI Server
    participant G as Google Gemini API
    participant F as File System
    
    C->>S: POST /process-voice/ (audio file)
    S->>F: Save temporary audio file
    S->>S: Generate placeholder transcription
    S->>G: Send text to Gemini API
    G-->>S: Return AI response
    S->>F: Delete temporary file
    S-->>C: Return JSON response
    
    Note right of S: Response includes:<br/>- Transcribed text<br/>- AI response<br/>- Model used
```

## Components Description

1. **Client**
   - Sends HTTP POST requests with audio files
   - Receives JSON responses with transcriptions and AI-generated text

2. **FastAPI Server**
   - Handles file uploads and validation
   - Manages temporary file storage
   - Coordinates with external APIs
   - Implements error handling and response formatting

3. **File System**
   - Temporarily stores uploaded audio files
   - Files are automatically cleaned up after processing

4. **Google Gemini API**
   - Processes text prompts
   - Generates contextual responses
   - Handles natural language understanding

## Data Flow

1. Client uploads an audio file to the `/process-voice/` endpoint
2. Server validates the file type and saves it temporarily
3. Server generates a placeholder transcription (in a real implementation, this would use a speech-to-text service)
4. Server sends the transcribed text to Google's Gemini API
5. Gemini processes the text and generates a response
6. Server formats the response and returns it to the client
7. Temporary files are cleaned up

## Error Handling

- Invalid file types are rejected immediately
- API rate limits and timeouts are handled gracefully
- Temporary files are always cleaned up, even if an error occurs
- Meaningful error messages are returned to the client
