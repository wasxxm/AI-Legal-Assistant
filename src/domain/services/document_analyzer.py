import base64
import json
from typing import Dict
from google.genai import types
import os
from asyncio import TimeoutError
from asyncio import wait_for
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.infrastructure.gemini import init_gemini_client, generate_content_stream
from src.utils.text_processing import clean_json_response, format_date
from src.core.config import GENERATE_CONFIG

async def analyze_legal_document(pdf_content: bytes) -> dict:
    """
    Analyze a legal document using Gemini AI
    
    Args:
        pdf_content (bytes): Content of the PDF file
        
    Returns:
        dict: Analyzed legal document data
    """
    try:
        # Initialize Gemini client
        client = init_gemini_client()
        
        # Convert PDF content to base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Create document part
        document = types.Part.from_bytes(
            data=base64.b64decode(pdf_base64),
            mime_type="application/pdf",
        )
        
        # Create instruction part
        instruction = types.Part.from_text(text="""IMPORTANT: Extract and structure ONLY information that is EXPLICITLY stated in the document. DO NOT add suggestions, interpretations, or information not directly present in the text.

Analyze this legal document and extract the following information in a structured JSON format. STRICTLY follow this exact structure:

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
    "constitutional_provisions": {
        "articles": ["string"],
        "fundamental_rights": ["string"],
        "statutory_provisions": ["string"]
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

STRICT INSTRUCTIONS:
1. Extract ONLY information that is EXPLICITLY stated in the document
2. DO NOT add any interpretations, suggestions, or information not directly present
3. Use exact quotes from the document where possible
4. If information is not found in the document, use empty string ("") or empty array ([])
5. Follow the exact JSON structure shown above
6. Ensure the date is in YYYY-MM-DD format
7. All text must be properly escaped for JSON
8. Maintain exact field names and capitalization
9. Return ONLY the JSON object, no additional text

Extract the following information ONLY IF EXPLICITLY STATED in the document:
1. Case number (exact as written)
2. Date of judgment (convert to YYYY-MM-DD)
3. Judges with their exact designations
4. Court details as mentioned
5. Parties and their counsel as listed
6. Procedural history as described
7. Laws cited with sections and interpretations given
8. Legal principles explicitly stated
9. Precedents cited with their stated relevance
10. Issues explicitly addressed
11. Arguments as presented by parties
12. Holdings as stated by the court
13. Relief granted as specified
14. Summary and implications as stated in the judgment
15. Bench composition details:
    - Type of bench (Full/Division/Single)
    - Any special designation
    - Number of judges
16. Case classification:
    - Type of case
    - Jurisdiction (Original/Appellate)
    - Whether it's an intra-court appeal
17. Hearing details:
    - All hearing dates mentioned
    - Date judgment was reserved
    - Date of announcement
18. Constitutional/statutory provisions:
    - Articles of Constitution cited
    - Fundamental rights discussed
    - Statutory provisions challenged
19. Previous history:
    - Lower court proceedings
    - Connected cases mentioned
    - Previous orders in same case""")
        
        # Prepare content
        contents = [
            types.Content(
                role="user",
                parts=[document, instruction]
            )
        ]
        
        # Generate analysis using streaming with timeout
        response_text = ""
        try:
            # Process stream in a thread pool
            def process_stream():
                stream = generate_content_stream(client, contents, GENERATE_CONFIG)
                text = ""
                for chunk in stream:
                    if chunk.text:
                        text += chunk.text
                return text
            
            # Run in thread pool with timeout
            with ThreadPoolExecutor() as executor:
                response_text = await wait_for(
                    asyncio.get_event_loop().run_in_executor(executor, process_stream),
                    timeout=30
                )
                
            # Clean and parse the response
            cleaned_response = clean_json_response(response_text)
            analysis_dict = json.loads(cleaned_response)
            
            # Format and structure the response
            formatted_dict = {
                "case_number": analysis_dict.get("case_number", ""),
                "date": format_date(analysis_dict.get("date")),
                "judges": [
                    {
                        "name": judge["name"] if isinstance(judge, dict) else judge.split(",")[0].strip(),
                        "designation": judge.get("designation") if isinstance(judge, dict) else (judge.split(",")[1].strip() if "," in judge else "")
                    }
                    for judge in analysis_dict.get("judges", [])
                ],
                "petitioner": {
                    "name": analysis_dict.get("petitioner", {}).get("name", ""),
                    "counsel": [{"name": c["name"], "designation": c.get("designation"), "firm": c.get("firm")} 
                              for c in analysis_dict.get("petitioner", {}).get("counsel", [])],
                    "designation": analysis_dict.get("petitioner", {}).get("designation")
                },
                "respondent": {
                    "name": analysis_dict.get("respondent", {}).get("name", ""),
                    "counsel": [{"name": c["name"], "designation": c.get("designation"), "firm": c.get("firm")} 
                              for c in analysis_dict.get("respondent", {}).get("counsel", [])],
                    "designation": analysis_dict.get("respondent", {}).get("designation")
                },
                "court": {
                    "name": analysis_dict.get("court", {}).get("name", ""),
                    "jurisdiction": analysis_dict.get("court", {}).get("jurisdiction"),
                    "bench_type": analysis_dict.get("court", {}).get("bench_type")
                },
                "procedural_history": {
                    "original_filing": analysis_dict.get("procedural_history", {}).get("original_filing"),
                    "previous_proceedings": analysis_dict.get("procedural_history", {}).get("previous_proceedings", []),
                    "current_stage": analysis_dict.get("procedural_history", {}).get("current_stage")
                },
                "laws": {
                    act: {
                        "sections": law_info["sections"],
                        "relevance": law_info.get("relevance"),
                        "interpretation": law_info.get("interpretation")
                    }
                    for act, law_info in analysis_dict.get("laws", {}).items()
                },
                "legal_principles": [
                    {
                        "principle": p["principle"],
                        "source": p.get("source"),
                        "application": p.get("application")
                    }
                    for p in analysis_dict.get("legal_principles", [])
                ],
                "precedents_cited": [
                    {
                        "case_name": p["case_name"],
                        "citation": p["citation"],
                        "relevance": p.get("relevance"),
                        "distinguished_or_followed": p.get("distinguished_or_followed")
                    }
                    for p in analysis_dict.get("precedents_cited", [])
                ],
                "issues": [
                    {
                        "question": i["question"],
                        "resolution": i.get("resolution"),
                        "reasoning": i.get("reasoning")
                    }
                    for i in analysis_dict.get("issues", [])
                ],
                "arguments": {
                    "petitioner": [
                        {
                            "point": a["point"],
                            "supporting_law": a.get("supporting_law"),
                            "supporting_precedents": a.get("supporting_precedents", [])
                        }
                        for a in analysis_dict.get("arguments", {}).get("petitioner", [])
                    ],
                    "respondent": [
                        {
                            "point": a["point"],
                            "supporting_law": a.get("supporting_law"),
                            "supporting_precedents": a.get("supporting_precedents", [])
                        }
                        for a in analysis_dict.get("arguments", {}).get("respondent", [])
                    ]
                },
                "holdings": [
                    {
                        "issue": h["issue"],
                        "decision": h["decision"],
                        "reasoning": h.get("reasoning")
                    }
                    for h in analysis_dict.get("holdings", [])
                ],
                "relief_granted": {
                    "type": analysis_dict.get("relief_granted", {}).get("type", ""),
                    "details": analysis_dict.get("relief_granted", {}).get("details"),
                    "conditions": analysis_dict.get("relief_granted", {}).get("conditions", [])
                },
                "summary": {
                    "brief": analysis_dict.get("summary", {}).get("brief", ""),
                    "key_findings": analysis_dict.get("summary", {}).get("key_findings", []),
                    "implications": analysis_dict.get("summary", {}).get("implications", [])
                },
                "bench_composition": {
                    "type": analysis_dict.get("bench_composition", {}).get("type", ""),
                    "special_designation": analysis_dict.get("bench_composition", {}).get("special_designation", ""),
                    "strength": analysis_dict.get("bench_composition", {}).get("strength", 0)
                },
                "case_classification": {
                    "type": analysis_dict.get("case_classification", {}).get("type", ""),
                    "jurisdiction": analysis_dict.get("case_classification", {}).get("jurisdiction", ""),
                    "intra_court_appeal": analysis_dict.get("case_classification", {}).get("intra_court_appeal", False)
                },
                "hearing_details": {
                    "hearing_dates": [
                        format_date(date_str)
                        for date_str in analysis_dict.get("hearing_details", {}).get("hearing_dates", [])
                        if date_str
                    ],
                    "reserved_on": format_date(analysis_dict.get("hearing_details", {}).get("reserved_on")),
                    "announced_on": format_date(analysis_dict.get("hearing_details", {}).get("announced_on"))
                },
                "constitutional_provisions": {
                    "articles": analysis_dict.get("constitutional_provisions", {}).get("articles", []),
                    "fundamental_rights": analysis_dict.get("constitutional_provisions", {}).get("fundamental_rights", []),
                    "statutory_provisions": analysis_dict.get("constitutional_provisions", {}).get("statutory_provisions", [])
                },
                "previous_history": {
                    "lower_court_details": [
                        {
                            "court": d.get("court", ""),
                            "case_number": d.get("case_number", ""),
                            "decision": d.get("decision", "")
                        }
                        for d in analysis_dict.get("previous_history", {}).get("lower_court_details", [])
                    ],
                    "connected_cases": analysis_dict.get("previous_history", {}).get("connected_cases", []),
                    "previous_orders": [
                        {
                            "date": format_date(o.get("date", "")),
                            "type": o.get("type", ""),
                            "details": o.get("details", "")
                        }
                        for o in analysis_dict.get("previous_history", {}).get("previous_orders", [])
                        if o.get("date")
                    ]
                }
            }

            # Clean up empty laws
            formatted_dict["laws"] = {k: v for k, v in formatted_dict["laws"].items() if v["sections"]}
            
            return formatted_dict
            
        except TimeoutError:
            raise Exception("Analysis timed out after 30 seconds")
            
    except Exception as e:
        raise Exception(f"Error analyzing document: {str(e)}")