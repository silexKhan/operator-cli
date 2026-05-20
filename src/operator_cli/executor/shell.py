import subprocess
from rich.console import Console

console = Console()

class ShellExecutor:
    @staticmethod
    def execute(command: str) -> str:
        """Executes a shell command and returns the output."""
        try:
            # safety check could be added here
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {str(e)}"
