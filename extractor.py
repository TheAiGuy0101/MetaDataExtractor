import docx

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Usage
file_path = 'Aug2022.docx'
extracted_text = extract_text_from_docx(file_path)

# Save the extracted text to a file
with open('extracted_text_Aug.txt', 'w', encoding='utf-8') as f:
    f.write(extracted_text)

print("Text has been extracted and saved to 'extracted_text.txt'")