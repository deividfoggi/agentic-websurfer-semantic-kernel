import logging
import sys
from semantic_kernel.agents import (
    Agent,
    ChatCompletionAgent,
    ChatHistoryAgentThread,
    MagenticOrchestration,
    StandardMagenticManager
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from utils.config import config
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from utils.prompthandler import get_prompt
from tools.shell import Shell
from tools.queryazmonitor import QueryAzureMonitor
from semantic_kernel.agents.runtime import InProcessRuntime

# Configure logging to output to console with detailed info
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("Agents")

class Agents:
    """
    Class to manage agents using MagenticOrchestration.
    """

    def __init__(self) -> None:
        logger.debug("Initializing Agents class.")
        self.magentic_orchestration = None
        self.runtime = InProcessRuntime()
        self.thread: ChatHistoryAgentThread = None

        logger.debug(f"Environment: {config.environment}")
        if config.environment == "dev":
            logger.debug("Using API key authentication for AzureChatCompletion.")
            self.chat_service = AzureChatCompletion(
                deployment_name=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key
            )
        else:
            logger.debug("Using Azure AD token authentication for AzureChatCompletion.")
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
        
    async def agents(self) -> list[Agent]:
        logger.debug("Building agent list.")

        self.aks_specialist_prompt = get_prompt("aks_specialist")
        logger.debug(f"AKS Specialist prompt: {self.aks_specialist_prompt}")
        aks_specialist = ChatCompletionAgent(
            name="aks_specialist",
            service=self.chat_service,
            instructions=self.aks_specialist_prompt,
            description="A Kubernetes and Azure AKS specialist agent that interprets natural language requests and executes 'kubectl' commands via the shell tool.",
            plugins=[Shell()],
        )

        self.azure_monitor_specialist_prompt = get_prompt("azure_monitor_specialist")
        logger.debug(f"Azure Monitor Specialist prompt: {self.azure_monitor_specialist_prompt}")
        azure_monitor_specialist = ChatCompletionAgent(
            name="azure_monitor_specialist",
            service=self.chat_service,
            instructions=self.azure_monitor_specialist_prompt,
            description="An Azure Monitor specialist agent that interprets natural language requests and provides insights based on Azure Monitor logs.",
            plugins=[QueryAzureMonitor()]
        )

        logger.debug("Agents created: aks_specialist, azure_monitor_specialist")
        return [aks_specialist, azure_monitor_specialist]
        
    async def run_task(self, payload: str) -> None:
        """
        Runs the agent's task with the provided payload.
        """
        logger.info(f"Starting run_task with payload: {payload}")
        try:
            magentic_orchestration = MagenticOrchestration(
                members=await self.agents(),
                manager=StandardMagenticManager(chat_completion_service=self.chat_service),
                agent_response_callback=self._agent_response_callback
            )

            logger.debug("Starting InProcessRuntime.")
            self.runtime.start()

            logger.debug("Invoking MagenticOrchestration.")
            orchestration_result = await magentic_orchestration.invoke(
                task=payload,
                runtime=self.runtime
            )

            logger.debug("Awaiting orchestration result.")
            value = await orchestration_result.get()
            logger.info(f"Final result: {value}")

            logger.debug("Stopping runtime when idle.")
            await self.runtime.stop_when_idle()
            logger.info("run_task completed successfully.")
        except Exception as e:
            logger.error(f"Exception in run_task: {e}", exc_info=True)

    @staticmethod
    def _agent_response_callback(message: ChatMessageContent) -> None:
        """Observer function to print the messages from the agents and manager."""
        logger = logging.getLogger("Agents.Callback")
        logger.info(f"Agent/Manager Message - **{message.name}**: {message.content}")