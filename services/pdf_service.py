import logging
import PyPDF2
from io import BytesIO

def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file
    """
    try:
        text_content = ""
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise Exception("PDF is encrypted and cannot be processed")
            
            num_pages = len(pdf_reader.pages)
            logging.info(f"Processing PDF with {num_pages} pages")
            
            # Extract text from each page
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Clean up the text
                        page_text = clean_extracted_text(page_text)
                        text_content += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    
                except Exception as e:
                    logging.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
            
            if not text_content.strip():
                raise Exception("No text could be extracted from the PDF")
            
            logging.info(f"Successfully extracted {len(text_content.split())} words from PDF")
            return text_content.strip()
            
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extract text from PDF provided as bytes
    """
    try:
        text_content = ""
        
        pdf_stream = BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        if pdf_reader.is_encrypted:
            raise Exception("PDF is encrypted and cannot be processed")
        
        num_pages = len(pdf_reader.pages)
        
        for page_num in range(num_pages):
            try:
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    page_text = clean_extracted_text(page_text)
                    text_content += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                
            except Exception as e:
                logging.warning(f"Error extracting text from page {page_num + 1}: {e}")
                continue
        
        return text_content.strip()
        
    except Exception as e:
        logging.error(f"PDF bytes extraction error: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def clean_extracted_text(text):
    """
    Clean up extracted text for better readability
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Fix common PDF extraction issues
    text = text.replace('\x00', '')  # Remove null characters
    text = text.replace('\ufffd', '')  # Remove replacement characters
    
    # Fix line breaks and spacing
    text = text.replace(' .', '.')
    text = text.replace(' ,', ',')
    text = text.replace(' !', '!')
    text = text.replace(' ?', '?')
    text = text.replace(' ;', ';')
    text = text.replace(' :', ':')
    
    # Add proper spacing after periods
    text = text.replace('.', '. ')
    text = text.replace('..', '.')  # Fix double periods
    text = ' '.join(text.split())  # Clean up extra spaces
    
    return text

def get_pdf_metadata(file_path):
    """
    Extract metadata from a PDF file
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'encrypted': pdf_reader.is_encrypted,
                'title': None,
                'author': None,
                'subject': None,
                'creator': None,
                'producer': None,
                'creation_date': None,
                'modification_date': None
            }
            
            # Extract document info if available
            if pdf_reader.metadata:
                doc_info = pdf_reader.metadata
                metadata.update({
                    'title': doc_info.get('/Title'),
                    'author': doc_info.get('/Author'),
                    'subject': doc_info.get('/Subject'),
                    'creator': doc_info.get('/Creator'),
                    'producer': doc_info.get('/Producer'),
                    'creation_date': doc_info.get('/CreationDate'),
                    'modification_date': doc_info.get('/ModDate')
                })
            
            return metadata
            
    except Exception as e:
        logging.error(f"PDF metadata extraction error: {e}")
        return {'error': str(e)}

def validate_pdf_file(file_path):
    """
    Validate if a file is a proper PDF
    """
    try:
        with open(file_path, 'rb') as file:
            # Check PDF header
            header = file.read(5)
            if header != b'%PDF-':
                return False, "File is not a valid PDF"
            
            # Try to read with PyPDF2
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                return False, "PDF contains no pages"
            
            return True, "Valid PDF file"
            
    except Exception as e:
        return False, f"PDF validation error: {str(e)}"
