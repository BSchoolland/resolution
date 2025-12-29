"""Click-based CLI for the resolution command."""

import subprocess
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from resolution import storage, coins, shop as shop_module, tui


console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Resolution 2026 - Daily habit tracker with gamified rewards.
    
    Run without arguments to start the morning routine.
    """
    if ctx.invoked_subcommand is None:
        # Run the morning TUI
        tui.run_morning_routine()


@cli.command()
def status():
    """Show current status and stats."""
    from resolution import bible, leetcode
    
    balance = coins.get_balance()
    bible_status = bible.get_reading_status()
    leetcode_stats = leetcode.get_stats()
    goals = storage.get_todays_goals()
    
    console.print()
    console.print(Panel(
        f"[bold yellow]💰 Coins: {balance:,}[/bold yellow]",
        title="Resolution 2026 Status",
        border_style="cyan"
    ))
    
    # Bible progress
    console.print()
    console.print("[bold cyan]📖 Bible Reading[/bold cyan]")
    console.print(f"  Progress: {bible_status['chapters_read']}/{bible_status['total']} chapters ({bible_status['percent_complete']}%)")
    if bible_status['behind'] > 0:
        console.print(f"  [yellow]Behind by {bible_status['behind']} chapters[/yellow]")
    elif bible_status['ahead'] > 0:
        console.print(f"  [green]Ahead by {bible_status['ahead']} chapters[/green]")
    
    # LeetCode stats
    console.print()
    console.print("[bold magenta]💻 LeetCode[/bold magenta]")
    console.print(f"  Total: {leetcode_stats['total_completed']} completed")
    console.print(f"  Easy: {leetcode_stats['easy']['completed']}/{leetcode_stats['easy']['total']}")
    console.print(f"  Medium: {leetcode_stats['medium']['completed']}/{leetcode_stats['medium']['total']}")
    console.print(f"  Hard: {leetcode_stats['hard']['completed']}/{leetcode_stats['hard']['total']}")
    
    # Today's goals
    if goals:
        console.print()
        console.print("[bold green]📋 Today's Goals[/bold green]")
        for i, goal in enumerate(goals, 1):
            console.print(f"  {i}. {goal}")
    
    console.print()


@cli.group(invoke_without_command=True)
@click.pass_context
def shop(ctx):
    """Manage the reward shop."""
    if ctx.invoked_subcommand is None:
        # Run interactive shop
        shop_module.interactive_shop()


@shop.command("list")
def shop_list():
    """List all shop items."""
    shop_module.list_items()


@shop.command("add")
@click.argument("name")
@click.argument("cost", type=int)
def shop_add(name: str, cost: int):
    """Add a new item to the shop."""
    shop_module.quick_add(name, cost)


@shop.command("delete")
@click.argument("item_id", type=int)
def shop_delete(item_id: int):
    """Delete an item from the shop."""
    if storage.delete_shop_item(item_id):
        console.print(f"[green]✓ Item {item_id} deleted![/green]")
    else:
        console.print(f"[red]Item {item_id} not found![/red]")


@shop.command("buy")
@click.argument("item_id", type=int)
def shop_buy(item_id: int):
    """Purchase an item from the shop."""
    success, message = storage.purchase_shop_item(item_id)
    if success:
        console.print(f"[green]✓ {message}[/green]")
    else:
        console.print(f"[red]{message}[/red]")


@cli.command()
def bye():
    """End of day routine - check goals and shutdown."""
    console.print()
    console.print(Panel(
        "[bold]🌙 End of Day Check-in[/bold]",
        border_style="blue"
    ))
    
    goals = storage.get_todays_goals()
    
    if not goals:
        console.print("[yellow]No goals were set today.[/yellow]")
    else:
        console.print()
        console.print("[bold]Which goals did you complete today?[/bold]")
        console.print()
        
        completed_count = 0
        for i, goal in enumerate(goals, 1):
            if Confirm.ask(f"  {i}. {goal}", default=True):
                completed_count += 1
        
        if completed_count > 0:
            earned = coins.award_goal_completed(completed_count)
            console.print()
            console.print(f"[green]🎉 Great job! Completed {completed_count}/{len(goals)} goals![/green]")
            console.print(f"[yellow]💰 +{earned} coins earned![/yellow]")
        else:
            console.print()
            console.print("[yellow]No goals completed. Tomorrow is a new day![/yellow]")
    
    # Show final balance
    balance = coins.get_balance()
    console.print()
    console.print(f"[bold]💰 Total coins: {balance:,}[/bold]")
    
    # Confirm shutdown
    console.print()
    if Confirm.ask("[red]Shut down computer now?[/red]", default=True):
        console.print()
        console.print("[dim]Shutting down... Goodnight! 🌙[/dim]")
        subprocess.run(["sudo", "shutdown", "now"])
    else:
        console.print("[dim]Shutdown cancelled. Goodnight! 🌙[/dim]")


@cli.command()
def reset():
    """Reset all progress (use with caution!)."""
    console.print("[bold red]⚠️  WARNING: This will reset ALL progress![/bold red]")
    console.print("This includes:")
    console.print("  - All coins")
    console.print("  - Bible reading progress")
    console.print("  - LeetCode completion history")
    console.print("  - Shop purchases")
    console.print()
    
    if Confirm.ask("[red]Are you absolutely sure?[/red]", default=False):
        if Confirm.ask("[red]Really really sure?[/red]", default=False):
            import os
            import shutil
            config_dir = storage.CONFIG_DIR
            if config_dir.exists():
                shutil.rmtree(config_dir)
            console.print("[green]✓ All progress has been reset.[/green]")
        else:
            console.print("[dim]Reset cancelled.[/dim]")
    else:
        console.print("[dim]Reset cancelled.[/dim]")


@cli.command()
def init():
    """Initialize the config with some default shop items."""
    storage.ensure_config_dir()
    
    # Add some default shop items if none exist
    items = storage.get_shop_items()
    if not items:
        defaults = [
            ("Coffee treat", 50),
            ("Nice lunch out", 150),
            ("New book", 300),
            ("Video game", 600),
            ("Weekend trip", 2000),
            ("New laptop", 10000),
        ]
        for name, cost in defaults:
            storage.add_shop_item(name, cost)
        console.print("[green]✓ Added default shop items![/green]")
    else:
        console.print("[yellow]Shop already has items.[/yellow]")
    
    shop_module.display_shop()


if __name__ == "__main__":
    cli()

