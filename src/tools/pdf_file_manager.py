import os
from semantic_kernel.functions import kernel_function
from PyPDF2 import PdfReader
from utils.config import config

class PdfFileManager:
    """
    PdfFileManager provides a kernel function to work with PDF files.
    """
    @kernel_function(name="read_pdf", description="Reads a PDF file and returns basic information and text content.")
    def read_pdf(self, file_path: str) -> dict:
        """
        Reads a PDF file from the output directory and returns basic information and text content.

        Args:
            file_path (str): The path (or filename) for the PDF file to read. Only the filename is used.

        Returns:
            dict: Dictionary with PDF info (number of pages, metadata, and first page text), or empty dict if reading fails.
        """
        output_dir = config.output_dir
        filename = os.path.basename(file_path)
        target_path = os.path.join(output_dir, filename)
        try:
            reader = PdfReader(target_path)
            info = {
                'num_pages': len(reader.pages),
                'metadata': dict(reader.metadata) if reader.metadata else {},
                'first_page_text': reader.pages[0].extract_text() if reader.pages else ''
            }
            return info
        except Exception:
            return {}
        
    @kernel_function(name="write_pdf", description="Write a PDF file to the output directory.")
    def write_pdf(self, filename: str, content: bytes) -> str:
        """
        Writes the provided content to a PDF file in the output directory.

        Args:
            filename (str): The name of the file to write.
            content (bytes): The content to write to the file.

        Returns:
            str: The path to the created file.
        """
        output_dir = config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path