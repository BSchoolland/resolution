"""Item shop for gamified rewards."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

from resolution import storage, coins


console = Console()


def display_shop() -> None:
    """Display the shop with all items."""
    items = storage.get_shop_items()
    balance = coins.get_balance()
    
    console.print()
    console.print(Panel(
        f"[bold yellow]💰 Your balance: {balance} coins[/bold yellow]",
        border_style="yellow"
    ))
    
    if not items:
        console.print("\n[dim]No items in the shop yet. Add some with 'resolution shop add'![/dim]\n")
        return
    
    table = Table(title="🏪 Item Shop", border_style="cyan")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Item", style="bold")
    table.add_column("Cost", justify="right", style="yellow")
    table.add_column("Status", justify="center")
    
    for item in items:
        cost = item["cost"]
        if item.get("purchased"):
            status = "[green]✓ Purchased[/green]"
        elif balance >= cost:
            status = "[cyan]Can afford![/cyan]"
        else:
            needed = cost - balance
            status = f"[red]Need {needed} more[/red]"
        
        table.add_row(
            str(item["id"]),
            item["name"],
            f"{cost:,} 🪙",
            status
        )
    
    console.print()
    console.print(table)
    console.print()


def interactive_shop() -> None:
    """Run interactive shop management."""
    while True:
        display_shop()
        
        console.print("[bold]Shop Actions:[/bold]")
        console.print("  [cyan]1[/cyan] - Add new item")
        console.print("  [cyan]2[/cyan] - Update item")
        console.print("  [cyan]3[/cyan] - Delete item")
        console.print("  [cyan]4[/cyan] - Purchase item")
        console.print("  [cyan]q[/cyan] - Quit")
        console.print()
        
        choice = Prompt.ask("Choose action", choices=["1", "2", "3", "4", "q"], default="q")
        
        if choice == "q":
            break
        elif choice == "1":
            add_item_interactive()
        elif choice == "2":
            update_item_interactive()
        elif choice == "3":
            delete_item_interactive()
        elif choice == "4":
            purchase_item_interactive()


def add_item_interactive() -> None:
    """Interactively add a new item."""
    console.print("\n[bold cyan]Add New Item[/bold cyan]")
    name = Prompt.ask("Item name")
    cost = IntPrompt.ask("Cost in coins")
    
    if cost < 0:
        console.print("[red]Cost must be positive![/red]")
        return
    
    item = storage.add_shop_item(name, cost)
    console.print(f"\n[green]✓ Added '{item['name']}' for {item['cost']} coins![/green]\n")


def update_item_interactive() -> None:
    """Interactively update an item."""
    items = storage.get_shop_items()
    if not items:
        console.print("[red]No items to update![/red]")
        return
    
    console.print("\n[bold cyan]Update Item[/bold cyan]")
    item_id = IntPrompt.ask("Item ID to update")
    
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        console.print("[red]Item not found![/red]")
        return
    
    console.print(f"Current: {item['name']} ({item['cost']} coins)")
    name = Prompt.ask("New name (leave empty to keep)", default="")
    cost_str = Prompt.ask("New cost (leave empty to keep)", default="")
    
    new_name = name if name else None
    new_cost = int(cost_str) if cost_str else None
    
    if storage.update_shop_item(item_id, name=new_name, cost=new_cost):
        console.print("[green]✓ Item updated![/green]\n")
    else:
        console.print("[red]Failed to update item![/red]\n")


def delete_item_interactive() -> None:
    """Interactively delete an item."""
    items = storage.get_shop_items()
    if not items:
        console.print("[red]No items to delete![/red]")
        return
    
    console.print("\n[bold cyan]Delete Item[/bold cyan]")
    item_id = IntPrompt.ask("Item ID to delete")
    
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        console.print("[red]Item not found![/red]")
        return
    
    if Confirm.ask(f"Delete '{item['name']}'?"):
        if storage.delete_shop_item(item_id):
            console.print("[green]✓ Item deleted![/green]\n")
        else:
            console.print("[red]Failed to delete item![/red]\n")


def purchase_item_interactive() -> None:
    """Interactively purchase an item."""
    items = storage.get_shop_items()
    if not items:
        console.print("[red]No items to purchase![/red]")
        return
    
    console.print("\n[bold cyan]Purchase Item[/bold cyan]")
    item_id = IntPrompt.ask("Item ID to purchase")
    
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        console.print("[red]Item not found![/red]")
        return
    
    if Confirm.ask(f"Purchase '{item['name']}' for {item['cost']} coins?"):
        success, message = storage.purchase_shop_item(item_id)
        if success:
            console.print(f"[green]✓ {message}[/green]\n")
        else:
            console.print(f"[red]{message}[/red]\n")


def quick_add(name: str, cost: int) -> None:
    """Quickly add an item without interaction."""
    item = storage.add_shop_item(name, cost)
    console.print(f"[green]✓ Added '{item['name']}' for {item['cost']} coins![/green]")


def list_items() -> None:
    """List all items in the shop."""
    display_shop()

