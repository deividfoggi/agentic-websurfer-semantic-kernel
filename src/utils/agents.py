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

class Agents:
    """
    Class to manage agents using MagenticOrchestration.
    """

    def __init__(self) -> None:
        self.magentic_orchestration = None
        self.runtime = InProcessRuntime()
        
        self.aks_specialist_prompt = get_prompt("aks_specialist")

        self.thread: ChatHistoryAgentThread = None

        if config.environment == "dev":
            self.chat_service = AzureChatCompletion(
                deployment_name=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version,
                endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_api_key
            )
        else:
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
           
        aks_specialist = ChatCompletionAgent(
            name="aks_specialist",
            service=self.chat_service,
            instructions=(
                self.aks_specialist_prompt
            ),
            description="A Kubernetes and Azure AKS specialist agent that interprets natural language requests and executes 'kubectl' commands via the shell tool.",
            plugins=[Shell()],
        )

        azure_monitor_specialist = ChatCompletionAgent(
            name="azure_monitor_specialist",
            service=self.chat_service,
            instructions=(
                self.azure_monitor_specialist_prompt
            ),
            description="An Azure Monitor specialist agent that interprets natural language requests and provides insights based on Azure Monitor logs.",
            plugins=[QueryAzureMonitor()]
        )

        return [aks_specialist, azure_monitor_specialist]
        
    async def run_task(self, payload: str) -> None:
        """
        Runs the agent's task with the provided payload.
        """
        magentic_orchestration = MagenticOrchestration(
            members = await self.agents(),
            manager=StandardMagenticManager(chat_completion_service=self.chat_service),
            agent_response_callback=self._agent_response_callback
        )

        self.runtime.start()

        orchestration_result = await magentic_orchestration.invoke(
            task=(
                payload
            ),
            runtime=self.runtime
        )

        value = await orchestration_result.get()
        print(f"Final result: {value}")

        await self.runtime.stop_when_idle()

    @staticmethod
    def _agent_response_callback(message: ChatMessageContent) -> None:
        """Observer function to print the messages from the agents and manager."""
        print(f"**{message.name}**\n{message.content}")