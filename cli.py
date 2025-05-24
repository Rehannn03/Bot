# cli.py
import click
import questionary
from pydantic import ValidationError
from config import Settings
from basic import Basic
from logger import logger

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1", prog_name="binance-bot")
def cli():
    """
    Binance Futures Testnet Trading Bot CLI

    Commands:
      market      Place a market order
      limit       Place a limit order
      oco         Place a One-Cancels-Other order
      interactive Launch interactive menu
    """
    pass

# … your existing market, limit, oco commands …

@cli.command("interactive", help="Launch an interactive, menu-driven interface")
def interactive():
    """Keep looping until the user exits."""
    try:
        settings = Settings()
    except ValidationError as ve:
        logger.error(ve)
        click.echo(f"Invalid configuration: {ve}")
        return

    bot = Basic(settings)

    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "📈 Market Order",
                "📉 Limit Order",
                "🔀 OCO Order",
                "📈 Stop-Limit Order",
                "📊 View Positions",
                "❌ Exit",
            ],
        ).ask()

        if action == "❌ Exit":
            click.echo("Goodbye!")
            break
        elif action == "📊 View Positions":
            try:
                positions = bot.get_positions()
                click.echo("Current Positions:")
                for pos in positions:
                    click.echo(f"{pos['symbol']}: {pos['positionAmt']} @ {pos['entryPrice']}")
            except Exception as e:
                click.echo(f"Error fetching positions: {e}")
            continue
        symbol = questionary.text("Symbol (e.g. BTCUSDT):").ask()
        side   = questionary.select("Side:", choices=["BUY", "SELL"]).ask()
        qty    = float(questionary.text("Quantity:").ask())

        # dispatch
        if action == "📈 Market Order":
            resp = bot.place_market_order(symbol, side, qty)

        elif action == "📉 Limit Order":
            price = float(questionary.text("Limit Price:").ask())
            resp = bot.place_limit_order(symbol, side, qty, price)

        elif action == "🔀 OCO Order":
            price      = float(questionary.text("Primary Limit Price:").ask())
            stop_price = float(questionary.text("Stop Trigger Price:").ask())
            resp = bot.place_oco_order(symbol, side, qty, price, stop_price)
        elif action == "📈 Stop-Limit Order":
            price      = float(questionary.text("Limit Price:").ask())
            stop_price = float(questionary.text("Stop Trigger Price:").ask())
            resp = bot.place_stop_limit_order(symbol, side, qty, price, stop_price)

        # show the raw JSON response
        click.echo(resp)

        if not questionary.confirm("Place another order?").ask():
            click.echo("Goodbye!")
            break

if __name__ == "__main__":
    cli(auto_envvar_prefix="BINANCE")
