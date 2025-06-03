import subprocess
from typing import Annotated
from semantic_kernel.functions import kernel_function

class Shell:
    """
    Classe para executar comandos em um shell Linux.
    """

    @kernel_function(description="Executa comandos em um shell Linux.")
    def shell(self, command: str) -> str:
        """
        Executa comandos em um shell linux.

        Parâmetros:
        - command (str): Comando a ser executado dentro do AKS. Exemplos: "kubectl get pods", "az login", etc.

        Retorno:
        - str: Saída do comando ou erro.
        """
        try:
            result = subprocess.run(
                command,
                shell=True, check=True, capture_output=True, text=True
            )

            return result.stdout.strip()
        
        except subprocess.CalledProcessError as e:
            return f"Erro ao executar comando: {e.stderr.strip()}"