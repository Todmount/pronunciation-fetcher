from rich.console import Console

console = Console()


def show_separator(symbol: str = "-", quantity: int = 60) -> None:
    console.print(symbol * quantity)
