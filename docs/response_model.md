# Legal Analysis Response Model

This document describes the structure of the response model used for legal document analysis.

## Overview

The response model is designed to capture comprehensive information from legal documents, with a focus on Pakistani law. It provides a structured format that enables easy access to various aspects of legal cases.

## Model Structure

### Basic Case Information
- `case_number`: String - The unique identifier for the case
- `date`: String - The date of judgment
- `judges`: Array of Objects
  - `name`: String - Name of the judge
  - `designation`: String - Designation/role of the judge

### Court Information
- `court`: Object
  - `name`: String - Name of the court
  - `jurisdiction`: String - Jurisdiction of the court
  - `bench_type`: String - Type of bench (e.g., "Single", "Division", "Full")

### Parties
Both `petitioner` and `respondent` have the same structure:
- Object
  - `name`: String - Name of the party
  - `designation`: String - Designation/role of the party
  - `counsel`: Array of Objects
    - `name`: String - Name of the counsel
    - `designation`: String - Designation of the counsel
    - `firm`: String - Law firm affiliation

### Procedural History
- `procedural_history`: Object
  - `original_filing`: String - Details of the original case filing
  - `previous_proceedings`: Array of Strings - List of previous proceedings
  - `current_stage`: String - Current stage of the case

### Laws
- `laws`: Object (Map)
  - Key: String - Name of the act/law
  - Value: Object
    - `sections`: Array of Strings - Referenced sections
    - `relevance`: String - Relevance to the case
    - `interpretation`: String - Court's interpretation

### Legal Principles
- `legal_principles`: Array of Objects
  - `principle`: String - The legal principle
  - `source`: String - Source of the principle
  - `application`: String - How it applies to the current case

### Precedents
- `precedents_cited`: Array of Objects
  - `case_name`: String - Name of the cited case
  - `citation`: String - Legal citation
  - `relevance`: String - Relevance to current case
  - `distinguished_or_followed`: String - Whether the precedent was distinguished or followed

### Issues
- `issues`: Array of Objects
  - `question`: String - The legal/factual question
  - `resolution`: String - How it was resolved
  - `reasoning`: String - Court's reasoning

### Arguments
- `arguments`: Object
  - `petitioner`: Array of Objects
    - `point`: String - Main argument point
    - `supporting_law`: String - Referenced laws
    - `supporting_precedents`: Array of Strings - Supporting case law
  - `respondent`: Array of Objects (same structure as petitioner)

### Holdings
- `holdings`: Array of Objects
  - `issue`: String - Issue addressed
  - `decision`: String - Court's decision
  - `reasoning`: String - Reasoning behind the decision

### Relief
- `relief_granted`: Object
  - `type`: String - Type of relief granted
  - `details`: String - Specific details of relief
  - `conditions`: Array of Strings - Conditions imposed

### Summary
- `summary`: Object
  - `brief`: String - Brief overview of the case
  - `key_findings`: Array of Strings - Key findings/points
  - `implications`: Array of Strings - Legal implications

## Usage Notes

1. All fields should be present in the response, even if empty
2. Use empty strings (`""`) for missing text fields
3. Use empty arrays (`[]`) for missing list fields
4. All text should be properly escaped for JSON
5. Dates should be in a consistent format
6. Citations should follow standard legal citation format

## Example

```json
{
  "case_number": "Civil Appeal No. 1234 of 2023",
  "date": "2023-12-25",
  "judges": [
    {
      "name": "Justice Ahmad Khan",
      "designation": "Chief Justice"
    }
  ],
  // ... other fields following the structure above
}
``` 