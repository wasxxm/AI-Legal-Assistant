# Legal Case Analysis API Documentation

## Overview

This API provides comprehensive analysis of Pakistani legal case documents using Google's Gemini AI. It extracts structured information from PDF documents of court judgments.

## Endpoints

### POST /analyze

Analyzes a legal case document (PDF) and returns structured information.

#### Request
- Method: POST
- Content-Type: multipart/form-data
- Body Parameter: file (PDF file)

#### Response

Returns a JSON object with the following structure:

```json
{
    "case_number": "string",
    "date": "YYYY-MM-DD",
    "judges": [
        {
            "name": "string",
            "designation": "string"
        }
    ],
    "court": {
        "name": "string",
        "jurisdiction": "string",
        "bench_type": "string"
    },
    "bench_composition": {
        "type": "string",
        "special_designation": "string",
        "strength": 0
    },
    "case_classification": {
        "type": "string",
        "jurisdiction": "string",
        "intra_court_appeal": false
    },
    "hearing_details": {
        "hearing_dates": ["YYYY-MM-DD"],
        "reserved_on": "YYYY-MM-DD",
        "announced_on": "YYYY-MM-DD"
    },
    "petitioner": {
        "name": "string",
        "designation": "string",
        "counsel": [
            {
                "name": "string",
                "designation": "string",
                "firm": "string"
            }
        ]
    },
    "respondent": {
        "name": "string",
        "designation": "string",
        "counsel": [
            {
                "name": "string",
                "designation": "string",
                "firm": "string"
            }
        ]
    },
    "procedural_history": {
        "original_filing": "string",
        "previous_proceedings": ["string"],
        "current_stage": "string"
    },
    "constitutional_provisions": {
        "articles": ["string"],
        "fundamental_rights": ["string"],
        "statutory_provisions": ["string"]
    },
    "laws": {
        "act_name": {
            "sections": ["string"],
            "relevance": "string",
            "interpretation": "string"
        }
    },
    "legal_principles": [
        {
            "principle": "string",
            "source": "string",
            "application": "string"
        }
    ],
    "precedents_cited": [
        {
            "case_name": "string",
            "citation": "string",
            "relevance": "string",
            "distinguished_or_followed": "string"
        }
    ],
    "issues": [
        {
            "question": "string",
            "resolution": "string",
            "reasoning": "string"
        }
    ],
    "arguments": {
        "petitioner": [
            {
                "point": "string",
                "supporting_law": "string",
                "supporting_precedents": ["string"]
            }
        ],
        "respondent": [
            {
                "point": "string",
                "supporting_law": "string",
                "supporting_precedents": ["string"]
            }
        ]
    },
    "holdings": [
        {
            "issue": "string",
            "decision": "string",
            "reasoning": "string"
        }
    ],
    "relief_granted": {
        "type": "string",
        "details": "string",
        "conditions": ["string"]
    },
    "summary": {
        "brief": "string",
        "key_findings": ["string"],
        "implications": ["string"]
    },
    "previous_history": {
        "lower_court_details": [
            {
                "court": "string",
                "case_number": "string",
                "decision": "string"
            }
        ],
        "connected_cases": ["string"],
        "previous_orders": [
            {
                "date": "YYYY-MM-DD",
                "type": "string",
                "details": "string"
            }
        ]
    }
}
```

#### Error Responses

```json
{
    "detail": {
        "detail": "string",
        "code": "string"
    }
}
```

Error Codes:
- INVALID_FILE_FORMAT: File is not a PDF
- PARSE_ERROR: Failed to parse the AI response
- INTERNAL_ERROR: Other internal errors

### GET /

Returns API information.

#### Response
```json
{
    "name": "Legal Case Analysis API",
    "version": "1.0.0",
    "description": "API for analyzing Pakistani legal cases using Google's Gemini AI"
}
```

## Notes

1. All dates are returned in ISO format (YYYY-MM-DD)
2. Missing text fields are returned as empty strings
3. Missing arrays are returned as empty arrays
4. The API extracts only information explicitly stated in the document
5. All text is properly escaped for JSON
6. Boolean fields default to false if not specified 