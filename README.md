# Automated Citation and Reference Verification Script

## Overview
This Python script automates the verification of citations and references in research reports, utilizing Mendable for accuracy checks and source management. It extracts references, verifies citations, identifies missing sources, and generates an accuracy report.

## Program Flow
1. **Input GPT Researcher Output**: Place the GPT Researcher output in the "reports" folder.
2. **Extract References**: The script extracts references from the report.
3. **Add References to Mendable**: Adds the extracted references to Mendable's data sources.
4. **Extract Text Based on References**: Retrieves parts of the text that are based on these references.
5. **Fact-Check Each Part**: Performs fact-checking for each extracted part of the text.
6. **Generate Report**:
    - Citations that need verification (information not found in the source).
    - Missing sources (sources mentioned in the text but not listed in the References).

## Setup and Usage

### Mendable
- Start a new projext.
- Generate an API key.
- Go to `Workshop > Customize Model > Edit Full Prompt`.
- Replace the default prompt by:

```
You are a fact checker who is part of the {company} team. Given the following verified sources and a question, answer the question saying True or False.
```

### Script
- Configure environment variables, install dependencies, and customize script paths.
- Run the script after placing text documents in the designated folder.
- Review the generated markdown reports for verification results.

## Output
- Markdown reports with verification results and an accuracy score for each processed document.

## Improvements
- **Clean Missing Sources Presentation**: Show it has text instead of a dictionary :) And have a nice sentence for when all sources are mentioned.
- **Include Source in Citations Needing Verification**: Each citation should reference its source for easy tracking.
- **Speed Optimization with `asyncio`**: Implement asynchronous processing to enhance script efficiency.
- **Source Duplication Check**: Avoid re-adding a source to Mendable if it already exists.