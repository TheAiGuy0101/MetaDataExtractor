import re
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        metadata = {}
        
        try:
            # Extract place and date
            
            date_match = re.search(r'DATED:\s*(\w+)\s+(\d{2}\.\d{2}\.\d{4})\s+BEFORE', case)
            if date_match:
                metadata['place'] = date_match.group(1)
                metadata['date'] = date_match.group(2)
            else:
                logger.warning(f"Failed to extract place and date for case {i}")
                metadata['place'] = ''
                metadata['date'] = ''
        except Exception as e:
            logger.warning(f"Error extracting place and date for case {i}: {str(e)}")
            metadata['place'] = ''
            metadata['date'] = ''
        
        try:
            # Extract bench name
            pattern = r"BEFORE\s+(THE HON’BLE.*)"
            bench_match = re.search(pattern, case, re.DOTALL)
            #bench_match = re.search(r'BEFORE\s+((?:THE HON\'BLE[^.]+[.]?\s*)+)', case, re.DOTALL)
            if bench_match:
                #bench_text = bench_match.group(1)
                #judges = re.findall(r'THE HON\'BLE\s+([^,\.]+)(?:[,\.]?\s*J\.?)?', bench_text)
                metadata['bench'] = bench_match.group() #' AND '.join(judges)
            else:
                logger.warning(f"Failed to extract bench for case {i}")
                metadata['bench'] = ''
        except Exception as e:
            logger.warning(f"Error extracting bench for case {i}: {str(e)}")
            metadata['bench'] = ''
        
        try:
            # Extract citation
            citation_match = re.search(r'\(\d{4}\)\s+\d+\s+ILRA\s+\d+', case)
            metadata['citation'] = citation_match.group() if citation_match else ''
        except Exception as e:
            logger.warning(f"Error extracting citation for case {i}: {str(e)}")
            metadata['citation'] = ''
        
        try:
            # Extract appellant
            appellant_match = re.search(r'(\w+)\s+\.\.\.Appellant', case)
            metadata['appellant'] = appellant_match.group(1) if appellant_match else ''
        except Exception as e:
            logger.warning(f"Error extracting appellant for case {i}: {str(e)}")
            metadata['appellant'] = ''
        
        try:
            # Extract opposite party
            opposite_party_match = re.search(r'Versus\s+(.*?)\s+\.\.\.Respondent', case, re.DOTALL)
            metadata['opposite_party'] = opposite_party_match.group(1).strip() if opposite_party_match else ''
        except Exception as e:
            logger.warning(f"Error extracting opposite party for case {i}: {str(e)}")
            metadata['opposite_party'] = ''
        
        try:
            # Extract counsels
            appellant_counsel_match = re.search(r'Counsel for the Appellant:\s+(.*?)\n(?:Counsel for|$)', case, re.DOTALL)
            metadata['appellant_counsel'] = appellant_counsel_match.group(1).strip() if appellant_counsel_match else ''
        except Exception as e:
            logger.warning(f"Error extracting appellant counsel for case {i}: {str(e)}")
            metadata['appellant_counsel'] = ''
        
        try:
            opposite_counsel_match = re.search(r'Counsel for the Opposite Party:\s+(.*?)$', case, re.DOTALL)
            metadata['opposite_counsel'] = opposite_counsel_match.group(1).strip() if opposite_counsel_match else ''
        except Exception as e:
            logger.warning(f"Error extracting opposite counsel for case {i}: {str(e)}")
            metadata['opposite_counsel'] = ''

        # Save metadata to MongoDB
        try:
            collection.insert_one(metadata)
        except Exception as e:
            logger.error(f"Failed to save metadata to MongoDB for case {i}: {str(e)}")

        # Save case to a separate file
        try:
            with open(f'case_{i}.txt', 'w', encoding='utf-8') as f:
                f.write(case)
        except Exception as e:
            logger.error(f"Failed to save case {i} to file: {str(e)}")

    print(f"Split {len(cases)} cases and saved metadata to MongoDB.")

# Usage
file_path = 'extracted_text_Aug.txt'
split_cases_and_extract_metadata(file_path)