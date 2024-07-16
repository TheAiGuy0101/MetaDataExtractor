import re
from pymongo import MongoClient

def split_cases_and_extract_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into cases
    cases = re.split(r'\n----------\s*\(\d{4}\)\s+\d+\s+ILRA\s+\d+', content)
    
    # Remove any empty cases
    cases = [case.strip() for case in cases if case.strip()]

    client = MongoClient('mongodb://localhost:27017/')
    db = client['legal_cases']
    collection = db['case_metadata']

    for i, case in enumerate(cases, 1):
        # Extract metadata
        metadata = {}
        lines = case.split('\n')
        
        # Safely extract citation
        citation_match = re.search(r'\(\d{4}\)\s+\d+\s+ILRA\s+\d+', case)
        metadata['citation'] = citation_match.group() if citation_match else ''

        metadata['jurisdiction'] = lines[1] if len(lines) > 1 else ''
        metadata['date_place'] = lines[2] if len(lines) > 2 else ''
        metadata['judges'] = ' '.join(lines[3:5]) if len(lines) > 4 else ''
        metadata['case_number'] = lines[5] if len(lines) > 5 else ''
        metadata['parties'] = lines[6] if len(lines) > 6 else ''

        # Save metadata to MongoDB
        collection.insert_one(metadata)

        # Save case to a separate file
        with open(f'case_{i}.txt', 'w', encoding='utf-8') as f:
            f.write(case)

    print(f"Split {len(cases)} cases and saved metadata to MongoDB.")

# Usage
file_path = 'extracted_text.txt'
split_cases_and_extract_metadata(file_path)

# Usage
file_path = 'extracted_text.txt'
split_cases_and_extract_metadata(file_path)