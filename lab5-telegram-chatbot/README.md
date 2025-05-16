# Telegram Bot with Weather and Ollama Integration

This application creates a Telegram bot that offers multiple services:
- Weather information using OpenWeather API
- Chat functionality using a local Ollama LLM instance
- Various utility commands

## Features

- `/start` - Initiates the bot
- `/help` - Shows all available commands
- `/weather <city>` - Gets weather information for a specified city
- `/chat <message>` - Explicitly chats with the Ollama LLM
- `/models` - Lists available Ollama models
- `/setmodel <model>` - Changes the Ollama model
- `/about` - Shows information about the bot
- Direct message handling - Any message not starting with a command is sent to the LLM

## Prerequisites

- Python 3.8+
- A Telegram Bot API key (from BotFather)
- An OpenWeather API key
- Ollama running locally on your machine

## Setup Instructions

1. Install the required packages:
   ```
   pip install python-telegram-bot requests python-dotenv
   ```

2. Create a `.env` file in the same directory with the following content:
   ```
   TELEGRAM_API_KEY=your_telegram_bot_token
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

3. Ensure Ollama is installed and running locally on the default port (11434)

4. Run the bot:
   ```
   python telegram_bot.py
   ```

## Customization

- The default Ollama model is set to "qwen3:32b" - you can change this in the code
- You can modify the OLLAMA_API_URL if your Ollama instance is running on a different port or machine

## Error Handling

The bot includes error handling for:
- Invalid city names in weather requests
- Connection issues with the Ollama API
- Missing command parameters