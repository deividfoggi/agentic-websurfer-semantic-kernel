from semantic_kernel.agents import StandardMagenticManager, MagenticOrchestration, ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureOpenAIChatCompletionClient
from semantic_kernet.contents import ChatMessageContent
from dotenv import load_dotenv
from utils.config import Config
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

class Agents:
    """
    Class to manage agents using MagenticOrchestration.
    """

    def __init__(self):
        self.magentic_orchestration = None

        if Config.environment == "dev":
            self.az_model_client = AzureOpenAIChatCompletionClient(
                azure_deployment=Config.aoai_deployment,
                model=Config.aoai_model,
                api_version=Config.aoai_version,
                azure_endpoint=Config.aoai_endpoint,
                api_key=Config.aoai_api_key
            )
        else:
            token_provider = get_bearer_token_provider(DefaultAzureCredential(), Config.llm_model_scope)
            self.az_model_client = AzureOpenAIChatCompletionClient(
                azure_deployment=Config.aoai_deployment,
                model=Config.aoai_model,
                api_version=Config.aoai_version,
                azure_endpoint=Config.aoai_endpoint,
                azure_ad_token_provider=token_provider
            )
            
