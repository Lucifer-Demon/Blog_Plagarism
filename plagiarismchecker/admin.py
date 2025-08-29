from django.contrib import admin
from .models import ReferenceDocument
from .models import PlagiarismHistory

admin.site.register(PlagiarismHistory)
from django.contrib import admin
from .models import ReferenceDocument
from docx import Document # For .docx files
import PyPDF2 # For .pdf files (Note: For newer PyPDF2 versions, it's PdfReader)
from io import BytesIO # To read file content in memory

# --- Custom ModelAdmin Class Definition (comes after imports) ---
class ReferenceDocumentAdmin(admin.ModelAdmin):
    # This method is called when an object is saved in the admin
    def save_model(self, request, obj, form, change):
        if obj.document_file: # Check if a file has been uploaded
            try:
                # Read the file content into memory
                file_content = obj.document_file.read()
                
                # Determine file type and extract text
                if obj.document_file.name.endswith('.txt'):
                    obj.content = file_content.decode('utf-8') # Decode text content
                elif obj.document_file.name.endswith('.docx'):
                    # Use BytesIO to pass the file content to python-docx
                    doc = Document(BytesIO(file_content))
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    obj.content = '\n'.join(full_text)
                elif obj.document_file.name.endswith('.pdf'):
                    # Use BytesIO to pass the file content to PyPDF2
                    pdf_file = BytesIO(file_content)
                    reader = PyPDF2.PdfReader(pdf_file) # Use PdfReader for modern PyPDF2
                    full_text = []
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        full_text.append(page.extract_text() or '') # Handle potentially empty text
                    obj.content = '\n'.join(full_text)
                else:
                    # Handle unsupported file types or leave content empty
                    obj.content = f"Unsupported file type: {obj.document_file.name}. Content not extracted."
                    self.message_user(request, f"Warning: Unsupported file type '{obj.document_file.name}'. Content not extracted.", level='WARNING')

            except Exception as e:
                obj.content = f"Error extracting content from file: {e}"
                self.message_user(request, f"Error processing file '{obj.document_file.name}': {e}", level='ERROR')
                # Log the error for debugging purposes
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error extracting content from ReferenceDocument file {obj.document_file.name}: {e}")
        
        # Always call the superclass's save_model to save the instance
        # This ensures the ReferenceDocument object (including its title and updated content) is saved
        super().save_model(request, obj, form, change)

admin.site.register(ReferenceDocument, ReferenceDocumentAdmin)

