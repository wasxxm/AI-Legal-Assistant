# Legal Case Analysis API

This API service uses Google's Gemini AI to analyze Pakistani legal case documents and extract structured information from them.

## Features

- PDF document analysis
- Extraction of key case information:
  - Case number
  - Date
  - Judges (with designations)
  - Petitioner and Respondent details (with legal representation)
  - Court information
  - Referenced laws (with descriptions)
  - Case summary
  - Arguments from both parties

## Setup Options

### Option 1: Docker (Recommended)

1. Install Docker and Docker Compose on your system
2. Clone the repository
3. Copy `.env.example` to `.env` and fill in your Google Cloud credentials:
   ```bash
   cp .env.example .env
   ```
4. Build and run the container:
   ```bash
   docker-compose up --build
   ```
   The API will be available at `http://localhost:8000`

### Option 2: Local Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Google Cloud credentials:
   ```bash
   cp .env.example .env
   ```
4. Run the API server:
   ```bash
   python main.py
   ```

## API Endpoints

### GET /
- Returns basic API information
- No parameters required

### POST /analyze
- Analyzes a legal case document
- Parameters:
  - `file`: PDF file (multipart/form-data)
- Returns structured analysis of the legal document

## Testing with Postman

1. Open Postman
2. Create a new POST request to `http://localhost:8000/analyze`
3. In the request body:
   - Select "form-data"
   - Add a key "file" of type "File"
   - Upload your PDF document
4. Send the request

## API Response Format

```json
{
    "case_number": "string",
    "date": "2023-12-20T00:00:00",
    "judges": [
        {
            "name": "string",
            "designation": "string"
        }
    ],
    "petitioner": {
        "name": "string",
        "representation": "string",
        "designation": "string"
    },
    "respondent": {
        "name": "string",
        "representation": "string",
        "designation": "string"
    },
    "court": "string",
    "laws": {
        "act_name": [
            {
                "section": "string",
                "description": "string"
            }
        ]
    },
    "summary": "string",
    "arguments": {
        "petitioner": ["string"],
        "respondent": ["string"]
    }
}
```

## Error Handling

The API returns appropriate HTTP status codes with detailed error messages:

```json
{
    "detail": "Error message",
    "code": "ERROR_CODE"
}
```

Common error codes:
- `INVALID_FILE_FORMAT`: When the uploaded file is not a PDF
- `PARSE_ERROR`: When the AI response cannot be parsed
- `INTERNAL_ERROR`: For other internal server errors

## Development

### Running Tests
```bash
# With Docker
docker-compose run api pytest

# Local
pytest
```

### Hot Reload
The API server supports hot reload during development:
- With Docker: Changes in the code will automatically reload the server
- Local: The server will reload on file changes

## Documentation

- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Environment Variables

Required environment variables in `.env`:
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Google Cloud region (e.g., "us-central1")

Optional:
- `GOOGLE_API_KEY`: If using Gemini API directly instead of Vertex AI 