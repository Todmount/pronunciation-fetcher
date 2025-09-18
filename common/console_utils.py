from rich.console import Console

console = Console()

def print_divider(symbol: str = "-", quantity: int = 80) -> None:
    console.print(symbol * quantity)
