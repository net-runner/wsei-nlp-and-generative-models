import os
import logging
import requests
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API URL
OLLAMA_MODEL = "qwen3:32b"  # Default model

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your multipurpose Telegram bot.\n\n"
        f"Use /help to see what I can do for you."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here are the commands you can use:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/weather <city> - Get weather information for a city\n"
        "/chat <message> - Chat with the Ollama LLM\n"
        "/models - List available Ollama models\n"
        "/setmodel <model> - Change the Ollama model\n"
        "/about - Information about this bot\n\n"
        "You can also just send a message to chat with the LLM directly!"
    )
    await update.message.reply_text(help_text)

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get weather information for a city."""
    if not context.args:
        await update.message.reply_text("Please provide a city name. Example: /weather London")
        return

    city = " ".join(context.args)
    await update.message.reply_text(f"Fetching weather data for {city}...")
    
    try:
        # Call OpenWeather API
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            # Extract data
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            
            # Format response
            weather_info = (
                f"🌍 Weather in {data['name']}, {data.get('sys', {}).get('country', '')}\n\n"
                f"🌤️ Condition: {weather_desc.capitalize()}\n"
                f"🌡️ Temperature: {temp}°C\n"
                f"🌡️ Feels like: {feels_like}°C\n"
                f"💧 Humidity: {humidity}%\n"
                f"💨 Wind speed: {wind_speed} m/s"
            )
            await update.message.reply_text(weather_info)
        else:
            error_message = f"Error: {data.get('message', 'City not found or API error')}"
            await update.message.reply_text(error_message)
    
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        await update.message.reply_text(f"Sorry, I couldn't fetch the weather information. Error: {str(e)}")

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Chat with the Ollama LLM using command."""
    if not context.args:
        await update.message.reply_text("Please provide a message. Example: /chat Hello, how are you?")
        return
    
    message = " ".join(context.args)
    await get_llm_response(update, message, context)

async def get_llm_response(update: Update, message: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Helper function to get response from Ollama LLM."""
    try:
        await update.message.reply_text("Thinking...")
        
        payload = {
            "model": context.bot_data.get("model", OLLAMA_MODEL),
            "prompt": message,
            "stream": False,
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("response", "No response from LLM")
            await update.message.reply_text(llm_response)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            logger.error(error_message)
            await update.message.reply_text(f"Sorry, I couldn't get a response from the LLM. Make sure Ollama is running locally.")
    
    except Exception as e:
        logger.error(f"LLM error: {e}")
        await update.message.reply_text(f"Error connecting to Ollama LLM: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages as chat with the LLM."""
    message = update.message.text
    await get_llm_response(update, message, context)

async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            if not models:
                await update.message.reply_text("No models found in your Ollama instance.")
                return
            
            model_list = "\n".join([f"• {model['name']}" for model in models])
            current_model = context.bot_data.get("model", OLLAMA_MODEL)
            
            await update.message.reply_text(
                f"Available models:\n{model_list}\n\n"
                f"Current model: {current_model}\n\n"
                f"To change model, use /setmodel <model_name>"
            )
        else:
            await update.message.reply_text(f"Error listing models: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        await update.message.reply_text(f"Error connecting to Ollama: {str(e)}")

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set Ollama model to use."""
    if not context.args:
        await update.message.reply_text("Please provide a model name. Example: /setmodel llama3")
        return
    
    model = context.args[0]
    context.bot_data["model"] = model
    await update.message.reply_text(f"Model set to: {model}")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Information about the bot."""
    about_text = (
        "🤖 *Telegram Bot with Weather and LLM*\n\n"
        "This bot combines weather information using OpenWeather API "
        "and conversational AI using your local Ollama instance.\n\n"
        "Features:\n"
        "• Weather forecasts for any city\n"
        "• Chat with various LLMs via Ollama\n"
        "• Multiple utility commands\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_API_KEY).build()
    
    

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("models", list_models))
    application.add_handler(CommandHandler("setmodel", set_model))
    application.add_handler(CommandHandler("about", about))
    
    # Add message handler for direct chat with LLM
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()
    logger.info("ZINGUS OFFLINE")

if __name__ == "__main__":
    main()