#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting TelegramAssistant AWS Setup..."

# 1. Update system and install required Python packages
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3-venv python3-pip screen

# 2. Clone the repository (if not already done)
if [ ! -d "UruellaBOT" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/JaimeCabary/UruellaBOT.git
fi

cd UruellaBOT

# 3. Create the .env file from the script arguments (or prompt if missing)
echo "🔒 Setting up environment variables..."
cat << EOF > .env
# Telegram Assistant Config
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"

# AI Providers
OPENAI_API_KEY="${OPENAI_API_KEY}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
GROQ_API_KEY="${GROQ_API_KEY}"

# Security
ALLOWED_USER_IDS="${ALLOWED_USER_IDS}"
EOF

# 4. Set up Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# 6. Start the bot in a background screen session
echo "🏃‍♂️ Starting the bot in the background..."
# Check if a screen session named 'telegram_bot' already exists and kill it if so
if screen -list | grep -q "telegram_bot"; then
    echo "Stopping existing bot instance..."
    screen -S telegram_bot -X quit
fi

# Need to run screen in detached mode and pass the command
screen -dmS telegram_bot bash -c "source venv/bin/activate && python bot.py"

echo "✅ Deployment Complete!"
echo "Your bot is now running in the background."
echo "To view the bot's logs, run: screen -r telegram_bot"
echo "To detach from the logs view (leave it running), press: Ctrl+A, then D"
