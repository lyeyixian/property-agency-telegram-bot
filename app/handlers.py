"""Telegram bot command handlers."""
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "👋 Welcome to the Property Agency Bot!\n\n"
        "I'm here to help you find your dream property. "
        "Use /help to see what I can do for you."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(
        "🏠 *Available Commands*\n\n"
        "/start — Welcome message\n"
        "/help — Show this help message\n"
        "/listings — Browse available property listings\n"
        "/contact — Get in touch with an agent\n"
        "/about — Learn more about our agency",
        parse_mode="Markdown",
    )


async def listings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /listings command."""
    await update.message.reply_text(
        "🏘️ *Current Listings*\n\n"
        "1. 3-bedroom condo in City Center — $500,000\n"
        "2. 4-bedroom bungalow in Suburbia — $750,000\n"
        "3. Studio apartment in Downtown — $200,000\n\n"
        "_More listings coming soon. Contact an agent for details!_",
        parse_mode="Markdown",
    )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /contact command."""
    await update.message.reply_text(
        "📞 *Contact Us*\n\n"
        "📧 Email: agent@propertyagency.com\n"
        "📱 Phone: +1-800-PROPERTY\n"
        "🌐 Website: www.propertyagency.com\n\n"
        "Our agents are available Mon–Fri, 9am–6pm.",
        parse_mode="Markdown",
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /about command."""
    await update.message.reply_text(
        "🏢 *About Property Agency*\n\n"
        "We are a leading property agency with over 20 years of experience "
        "helping clients buy, sell, and rent properties.\n\n"
        "Our team of dedicated agents is committed to finding you the perfect home.",
        parse_mode="Markdown",
    )
