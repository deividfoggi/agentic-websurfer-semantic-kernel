import os
from semantic_kernel.functions import kernel_function
from PyPDF2 import PdfReader

class FileManager:
    """
    FileManager provides a kernel function to work with files.
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

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        output_dir = os.path.join(project_root, 'output')
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
    
    @kernel_function(name="write_text_file", description="Writes text to a file in the output directory.")
    def write_text_file(self, filename: str, content: str) -> str:
        """
        Writes the provided content to a text file in the output directory.

        Args:
            filename (str): The name of the file to write.
            content (str): The content to write to the file.

        Returns:
            str: The path to the created file.
        """
        #project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        output_dir = os.path.join('/Users/deividfoggi/Documents/', 'playwright-output')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    @kernel_function(name="read_text_file", description="Reads a text file and returns its content.")
    def read_text_file(self, filename: str) -> str:
        """
        Reads a text file from the output directory and returns its content.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file, or an empty string if reading fails.
        """
        #project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        output_dir = os.path.join('/Users/deividfoggi/Documents/', 'playwright-output')
        file_path = os.path.join(output_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ''