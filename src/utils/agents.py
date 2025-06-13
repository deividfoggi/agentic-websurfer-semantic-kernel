import sys
from semantic_kernel.agents import (
    Agent,
    ChatCompletionAgent,
    ChatHistoryAgentThread,
    MagenticOrchestration,
    StandardMagenticManager,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.mcp import MCPSsePlugin
from semantic_kernel.contents import ChatMessageContent, ChatHistory
from semantic_kernel import Kernel
from utils.Config import config
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from utils.prompthandler import get_prompt
from tools.file_manager import FileManager
from utils.token_utils import count_tokens
from tools.utilities_belt import UtilitiesBelt
from utils.kernel import KernelService
import logging

#Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("Agents")

class Agents:
    """
    Class to manage agents using direct chat completion.
    """

    def __init__(self) -> None:
        self.web_surfer_agent = None
        kernel_service = KernelService()
        self.kernel = kernel_service.get_kernel()
        self.chat_service = kernel_service.get_chat_service()
        self.magentic_orchestration = None
        self.runtime = InProcessRuntime()
        self.thread: ChatHistoryAgentThread = None
        self.initialize()

    async def initialize(self) -> None:
        self.mcp_plugin = MCPSsePlugin(
            name="playwright",
            description="Playwright MCP Plugin",
            url="http://localhost:9339/sse"
        )
        await self.mcp_plugin.connect()
        logger.info("Initializing MCP plugin...")
        self.kernel.add_plugin(self.mcp_plugin)
        self.kernel.add_plugin(FileManager())
        self.kernel.add_plugin(UtilitiesBelt())
        logger.info("Tools added to the kernel.")

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

    async def get_agents(self) -> list[Agent]:
        logger.debug("Creating agents...")
        web_surfer_prompt = get_prompt("web_surfer_specialist")
        web_surfer_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="web_surfer_specialist",
            service=self.chat_service,
            instructions=web_surfer_prompt,
            description="Um especialista em navegação na web que utiliza as ferramentas Playwright MCP para navegar e extrair conteúdo de páginas da internet.",
        )

        facts_checker_prompt = get_prompt("fact_checker")
        facts_checker_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="fact_checker",
            service=self.chat_service,
            instructions=facts_checker_prompt,
            description="Um especialista em verificação de fatos que utiliza várias ferramentas e recursos para validar informações.",
        )
        return [web_surfer_agent, facts_checker_agent]

    async def run_task(self, payload: str) -> None:
        try:
            await self.mcp_plugin.connect()
            members = await self.get_agents()
            runtime = InProcessRuntime()
            main_prompt = get_prompt("main_prompt")
            try:
                runtime.start()
                payload += main_prompt

                # Truncate chat history if needed
                if self.thread:
                    self.thread = self._truncate_chat_history(
                        self.thread, max_tokens=100000, model="gpt-4o"
                    )

                magentic_orchestration = MagenticOrchestration(
                    members=members,
                    manager=StandardMagenticManager(chat_completion_service=self.chat_service),
                    agent_response_callback=self._agent_response_callback
                )
                orchestration_result = await magentic_orchestration.invoke(
                    task=payload,
                    runtime=runtime,
                )
                value = await orchestration_result.get()
                logger.info(f"Task completed successfully: {value}")
            finally:
                await runtime.stop_when_idle()
                logger.info("Runtime stopped.")
        except Exception as e:
            if "context_length_exceeded" in str(e):
                logger.error("Token limit exceeded. Trimming chat history and retrying...")
                if self.thread:
                    self.thread = self._truncate_chat_history(
                        self.thread, max_tokens=80000, model="gpt-4o"
                    )
            else:
                logger.error(f"Error in run_task: {e}")

    @staticmethod
    def _agent_response_callback(message: ChatMessageContent, is_final: bool = False) -> None:
       """Observer function to print the messages from the agents and manager."""
       logger = logging.getLogger("Agents.Callback")
       logger.info(f"Agent/Manager Message - **{message.name}**: {message.content}")

    def _truncate_chat_history(self, chat_history: ChatHistory, max_tokens: int = 100000, model: str = "gpt-4o") -> ChatHistory:
        """Trim chat history to fit within a token budget."""
        trimmed = ChatHistory()
        total_tokens = 0
        for message in reversed(chat_history):
            message_text = getattr(message, "content", "")
            message_tokens = count_tokens(message_text, model=model)
            if total_tokens + message_tokens > max_tokens:
                break
            trimmed.insert(0, message)
            total_tokens += message_tokens
        return trimmed