import re
import os
import PyPDF2
import docx 

# Country codes dictionary
country_codes = {
    '+1': 'United States/Canada',
    '+44': 'United Kingdom',
    '+91': 'India',
    '+61': 'Australia',
    '+81': 'Japan',
    '+49': 'Germany',
    '+33': 'France',
    '+86': 'China',
    '+39': 'Italy',
    '+7': 'Russia',
    '+55': 'Brazil'
}

# Phone number regex
phone_regex = re.compile(r'''
    (
        (\+?\d{1,3})?                # Country code (optional)
        (\s|-|\.)?                   # Separator
        (\(?\d{2,5}\)?)              # Area code
        (\s|-|\.)?                   # Separator
        (\d{3,5})                    # First 3–5 local digits
        (\s|-|\.)                    # Separator
        (\d{4})                      # Last 4 digits
        (\s*(ext|x|ext.)\s*\d{2,5})? # Extension (optional)
    )
''', re.VERBOSE | re.IGNORECASE)

# Email regex
email_regex = re.compile(r'''
    (
        [a-zA-Z0-9._%+-]+
        @
        [a-zA-Z0-9.-]+
        \.[a-zA-Z]{2,10}
    )
''', re.VERBOSE)

def normalize_phone(country, area, first, last, ext):
    country = (country or '').replace(' ', '')
    if not country.startswith('+'):
        if country:
            country = '+' + country
        else:
            country = '+1'

    local = f"{area.replace('(', '').replace(')', '')}{first}{last}"
    local = re.sub(r'\D', '', local)
    if len(local) > 10:
        local = local[-10:]
    elif len(local) < 10:
        local = local.rjust(10, '0')

    country_name = country_codes.get(country, 'Unknown')
    full_number = f"{country} {local}"
    if ext:
        ext_clean = ext.strip().replace('ext.', 'ext').replace('x', 'ext')
        full_number += f" {ext_clean}"
    return f"{full_number} ({country_name})"

def extract_contacts(text):
    matches = []
    for groups in phone_regex.findall(text):
        country = groups[1]
        area = groups[3]
        first = groups[5]
        last = groups[7]
        extension = groups[8]
        normalized = normalize_phone(country, area, first, last, extension)
        matches.append(normalized)

    for groups in email_regex.findall(text):
        matches.append(groups[0])

    return matches

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def read_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def main():
    file_path = input("Enter the path to the .txt, .pdf, or .docx file: ").strip()

    if not os.path.isfile(file_path):
        print("File not found.")
        return

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        text = read_txt(file_path)
    elif ext == '.pdf':
        text = read_pdf(file_path)
    elif ext == '.docx':
        text = read_docx(file_path)
    else:
        print("Unsupported file type. Only .txt, .pdf, and .docx are supported.")
        return

    results = extract_contacts(text)
    if results:
        print("Extracted Contacts:")
        print('\n'.join(results))
        with open("extractedContacts.txt", "w", encoding='utf-8') as f:
            f.write('\n'.join(results))
        print("Saved to 'extractedContacts.txt'")
    else:
        print("No contacts found.")

if __name__ == "__main__":
    main()
