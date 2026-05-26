import subprocess
from rich.console import Console

console = Console()

class ShellExecutor:
    @staticmethod
    def execute(command: str) -> str:
        """Executes a shell command and returns the output."""
        try:
            # 명령어 안전성 사전 검사 (Safety Check)
            danger_keywords = ["rm -rf", "mkfs", "sudo dd", "shutdown", ":(){:|:&};:"]
            # 단순 차단뿐 아니라 경고 처리를 위한 보안 메커니즘
            for kw in danger_keywords:
                if kw in command:
                    return f"Error: Command execution blocked due to safety protocols. Detected critical keyword: '{kw}'."
            
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
