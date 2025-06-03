from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient
from datetime import datetime, timedelta
import json
from typing import Annotated
from semantic_kernel.functions import kernel_function

class DateTimeEncoder(json.JSONEncoder):
    """
    Classe para serializar objetos datetime em JSON.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@kernel_function(description="Executa uma query em um recurso no Azure Monitor workspace em busca de logs. Deve informar a query Kusto, o intervalo de tempo e o ID do workspace do Azure Monitor.")
class QueryAzureMonitor:
    """
    Classe para executar queries no Azure Monitor.
    """

    def __init__(self) -> None:
        self.credential = DefaultAzureCredential()
        self.client = LogsQueryClient(self.credential)
        #workspace_id = Config.azm_workspace_id
    
    async def query(self, query: str, time_span: timedelta, workspace_id: str) -> str:
        """
        Executa uma query em um recurso no Azure Monitor workspace em busca de logs.

        Parâmetros:
        - resource_id (str): ID do recurso a ser consultado.
        - query (str): Query Kusto a ser executada.
        - time_span (timedelta): Intervalo de tempo para a consulta.
        - workspace_id (str): ID do workspace do Azure Monitor.
        Retorno:
        - json: Saída do comando ou erro.
        """
        results = []

        try:
            response = await self.client.query_workspace(
                workspace_id=workspace_id,
                query=query,
                timespan=time_span
            )

            if response.tables:
                for table in response.tables:
                    for row in table.rows:
                        row_dict = dict(zip(table.columns, row))
                        results.append(row_dict)

            query_result = json.dumps({"status": "success", "logs": results}, cls=DateTimeEncoder)
            return query_result

        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
        finally:
            await self.credential.close()
            await self.client.close()