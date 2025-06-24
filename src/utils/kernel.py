import logging
import sys
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from utils.config import config

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("KernelService")

class KernelService:
    """
    Class to manage kernel and chat completion services.
    """
    
    def __init__(self) -> None:
        self.kernel = Kernel()
        self.chat_service = None
        self._initialize_chat_service()

    def _initialize_chat_service(self) -> None:
        if config.environment == "dev":
            logger.info("Using Azure OpenAI service with API key for development environment.")
            self.chat_service = AzureChatCompletion(
                deployment_name=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key
            )
        else:
            logger.info("Using Azure OpenAI service with DefaultAzureCredential for production environment.")
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                config.llm_model_scope
            )
            self.chat_service = AzureChatCompletion(
                deployment_name=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version,
                endpoint=config.azure_openai_endpoint,
                ad_token_provider=token_provider
            )

        logger.info("Adding chat service to the kernel...")
        self.kernel.add_service(self.chat_service)

    def get_kernel(self) -> Kernel:
        """
        Returns the initialized kernel with chat service.
        """
        return self.kernel

    def get_chat_service(self) -> AzureChatCompletion:
        """
        Returns the initialized chat service.
        """
        return self.chat_service