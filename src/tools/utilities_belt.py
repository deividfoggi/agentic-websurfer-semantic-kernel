import uuid
from datetime import datetime
from semantic_kernel.functions import kernel_function

class UtilitiesBelt:
    @kernel_function(name="generate_guid", description="Generates a new GUID")
    def generate_guid(self) -> str:
        """
        Generates a new GUID
        Returns:
            str: A new GUID as string
        """
        return str(uuid.uuid4())

    @kernel_function(name="generate_timestamp", description="Generates a timestamp")
    def generate_timestamp(self) -> str:
        """
        Creates a timestamp in the format YYYYMMDD-HHMMSS
        Returns:
            str: Formatted timestamp string
        """
        return datetime.now().strftime("%Y%m%d-%H%M%S")