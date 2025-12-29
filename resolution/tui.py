"""Morning TUI - the main interactive interface using Rich."""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

from resolution import storage, bible, leetcode, coins, shop


console = Console()


def clear_screen():
    """Clear the terminal screen."""
    console.clear()


def print_header():
    """Print the app header."""
    header = Text()
    header.append("╔══════════════════════════════════════════════════════════════╗\n", style="bold cyan")
    header.append("║           ", style="bold cyan")
    header.append("🌅 RESOLUTION 2026 ", style="bold yellow")
    header.append("- Daily Habit Tracker", style="bold white")
    header.append("           ║\n", style="bold cyan")
    header.append("╚══════════════════════════════════════════════════════════════╝", style="bold cyan")
    console.print(Align.center(header))
    console.print()


def print_progress_bar(current_step: int, total_steps: int = 3):
    """Print a visual progress bar for the morning routine."""
    steps = ["Goals", "Bible", "LeetCode"]
    
    progress_text = Text()
    for i, step in enumerate(steps):
        if i < current_step:
            progress_text.append(f" ✓ {step} ", style="bold green")
        elif i == current_step:
            progress_text.append(f" ● {step} ", style="bold yellow")
        else:
            progress_text.append(f" ○ {step} ", style="dim")
        
        if i < len(steps) - 1:
            progress_text.append("→", style="dim")
    
    console.print(Panel(Align.center(progress_text), border_style="blue", title="Progress"))
    console.print()


def step_goals() -> list[str]:
    """Step 1: Get today's goals from the user."""
    clear_screen()
    print_header()
    print_progress_bar(0)
    
    console.print(Panel(
        "[bold]What are your goals for today?[/bold]\n\n"
        "[dim]Enter a comma-separated list of things you want to accomplish.[/dim]",
        title="📋 Step 1: Daily Goals",
        border_style="green",
    ))
    console.print()
    
    goals_input = Prompt.ask("[cyan]Goals[/cyan]")
    goals = [g.strip() for g in goals_input.split(",") if g.strip()]
    
    if goals:
        storage.save_todays_goals(goals)
        console.print()
        console.print("[green]✓ Goals saved![/green]")
        for i, goal in enumerate(goals, 1):
            console.print(f"  {i}. {goal}")
    else:
        console.print("[yellow]No goals entered. You can add them later![/yellow]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    return goals


def step_bible() -> int:
    """Step 2: Bible reading check. Returns coins earned."""
    clear_screen()
    print_header()
    print_progress_bar(1)
    
    status = bible.get_reading_status()
    position = bible.get_current_position()
    readings = bible.get_todays_reading()
    
    # Build the Bible panel content
    content = Text()
    content.append(f"📖 Currently at: ", style="bold")
    content.append(f"{position['book']} {position.get('chapter', 1)}\n", style="cyan")
    content.append(f"📊 Progress: ", style="bold")
    content.append(f"{status['chapters_read']}/{status['total']} chapters ", style="white")
    content.append(f"({status['percent_complete']}%)\n", style="dim")
    
    if status['behind'] > 0:
        content.append(f"⚠️  Behind by: ", style="bold yellow")
        content.append(f"{status['behind']} chapters\n", style="yellow")
    elif status['ahead'] > 0:
        content.append(f"🌟 Ahead by: ", style="bold green")
        content.append(f"{status['ahead']} chapters\n", style="green")
    
    content.append(f"\n📚 Today's reading:\n", style="bold")
    for reading in readings:
        content.append(f"   • {reading}\n", style="cyan")
    
    console.print(Panel(
        content,
        title="📖 Step 2: Bible Reading",
        border_style="blue",
    ))
    console.print()
    
    total_coins = 0
    chapters_today = status['chapters_today']
    
    # Ask if they completed today's reading
    did_read = Confirm.ask(f"Did you read today's {chapters_today} chapters?", default=True)
    
    if did_read:
        bible.record_reading(chapters_today)
        earned = coins.award_bible_reading(chapters_today)
        total_coins += earned
        console.print(f"[green]✓ Great job! +{earned} coins for {chapters_today} chapters![/green]")
    else:
        console.print("[yellow]No worries, try to catch up when you can![/yellow]")
    
    # If behind, ask about catch-up reading
    if status['behind'] > 0:
        console.print()
        console.print(f"[yellow]You're {status['behind']} chapters behind schedule.[/yellow]")
        extra = Confirm.ask("Did you read any extra chapters to catch up?", default=False)
        
        if extra:
            extra_count = IntPrompt.ask("How many extra chapters?", default=1)
            if extra_count > 0:
                bible.record_reading(extra_count)
                earned = coins.award_bible_reading(extra_count, is_catchup=True)
                total_coins += earned
                console.print(f"[green]✓ Awesome! +{earned} coins for {extra_count} catch-up chapters![/green]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    return total_coins


def step_leetcode() -> int:
    """Step 3: LeetCode problem selection. Returns coins earned."""
    clear_screen()
    print_header()
    print_progress_bar(2)
    
    # Show current stats
    stats = leetcode.get_stats()
    
    stats_text = Text()
    stats_text.append(f"🏆 Total completed: {stats['total_completed']}\n", style="bold")
    stats_text.append(f"   Easy: {stats['easy']['completed']}/{stats['easy']['total']} ", style="green")
    stats_text.append(f"| Medium: {stats['medium']['completed']}/{stats['medium']['total']} ", style="yellow")
    stats_text.append(f"| Hard: {stats['hard']['completed']}/{stats['hard']['total']}", style="red")
    
    console.print(Panel(
        stats_text,
        title="💻 Step 3: LeetCode Practice",
        border_style="magenta",
    ))
    console.print()
    
    # Ask for difficulty
    console.print("[bold]What difficulty do you want today?[/bold]")
    console.print("  [green]1[/green] - Easy (10 coins)")
    console.print("  [yellow]2[/yellow] - Medium (25 coins)")
    console.print("  [red]3[/red] - Hard (50 coins)")
    console.print()
    
    choice = Prompt.ask("Difficulty", choices=["1", "2", "3"], default="2")
    difficulty = {"1": "easy", "2": "medium", "3": "hard"}[choice]
    
    # Get random problems
    problems = leetcode.get_random_problems(difficulty, 3)
    
    if not problems:
        console.print(f"[yellow]No more {difficulty} problems available! You've done them all! 🎉[/yellow]")
        Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        return 0
    
    console.print()
    console.print(f"[bold]Here are 3 {difficulty} problems to choose from:[/bold]")
    console.print()
    
    table = Table(box=box.ROUNDED)
    table.add_column("#", style="dim", width=3)
    table.add_column("ID", width=6)
    table.add_column("Problem", style="cyan")
    
    for i, problem in enumerate(problems, 1):
        table.add_row(
            str(i),
            str(problem['frontend_id']),
            problem['title']
        )
    
    console.print(table)
    console.print()
    
    # Let user pick
    valid_choices = [str(i) for i in range(1, len(problems) + 1)]
    pick = Prompt.ask("Which one? (number)", choices=valid_choices, default="1")
    selected = problems[int(pick) - 1]
    
    # Open in browser
    url = leetcode.open_problem(selected['slug'])
    console.print()
    console.print(f"[green]✓ Opening: {selected['title']}[/green]")
    console.print(f"[dim]{url}[/dim]")
    
    # Mark as completed and award coins
    leetcode.mark_problem_done(selected['id'], difficulty)
    earned = coins.REWARDS.get(f"leetcode_{difficulty}", 10)
    
    console.print()
    console.print(f"[bold green]🪙 +{earned} coins earned![/bold green]")
    
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
    
    return earned


def show_rewards_summary(bible_coins: int, leetcode_coins: int):
    """Show a summary of coins earned and the shop."""
    clear_screen()
    print_header()
    
    total_earned = bible_coins + leetcode_coins
    balance = coins.get_balance()
    
    # Reward summary
    summary = Text()
    summary.append("🎉 Morning Routine Complete! 🎉\n\n", style="bold yellow")
    summary.append(f"Bible Reading: +{bible_coins} coins\n", style="green")
    summary.append(f"LeetCode:      +{leetcode_coins} coins\n", style="green")
    summary.append("─" * 25 + "\n", style="dim")
    summary.append(f"Total Earned:  +{total_earned} coins\n\n", style="bold green")
    summary.append(f"💰 Current Balance: {balance} coins", style="bold yellow")
    
    console.print(Panel(
        Align.center(summary),
        title="🏆 Daily Rewards",
        border_style="yellow",
    ))
    console.print()
    
    # Show shop
    shop.display_shop()
    
    # Ask if they want to purchase anything
    items = storage.get_shop_items()
    affordable = [i for i in items if not i.get("purchased") and i["cost"] <= balance]
    
    if affordable:
        console.print("[cyan]You can afford some items! Want to purchase something?[/cyan]")
        if Confirm.ask("Visit shop?", default=False):
            shop.purchase_item_interactive()
    
    console.print()
    console.print("[bold green]Have a great day! Remember your goals:[/bold green]")
    goals = storage.get_todays_goals()
    for i, goal in enumerate(goals, 1):
        console.print(f"  {i}. {goal}")
    
    console.print()
    console.print("[dim]Run 'resolution bye' tonight to check off completed goals![/dim]")
    console.print()


def run_morning_routine():
    """Run the complete morning routine."""
    # Mark that we ran today
    storage.mark_ran_today()
    storage.ensure_config_dir()
    
    try:
        # Step 1: Goals
        goals = step_goals()
        
        # Step 2: Bible
        bible_coins = step_bible()
        
        # Step 3: LeetCode
        leetcode_coins = step_leetcode()
        
        # Show summary and shop
        show_rewards_summary(bible_coins, leetcode_coins)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Morning routine interrupted. See you tomorrow![/yellow]")
        sys.exit(0)


def run_if_needed() -> bool:
    """Check if we should run and run if needed. Returns True if ran."""
    from datetime import datetime
    
    # Check if after 6am
    now = datetime.now()
    if now.hour < 6:
        return False
    
    # Check if already ran today
    if storage.ran_today():
        return False
    
    # Run the routine
    run_morning_routine()
    return True

