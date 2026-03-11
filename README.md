# 🚀 Telegram Virtual Assistant (n8n Alternative)

A custom, Python-based Virtual Assistant for Telegram that runs entirely on your own server (or AWS instance). It supports multiple AI engines (OpenAI, Claude 3, Llama via Groq) and will be extended to automate Google Workspace tasks (Calendar, Gmail, Sheets, Docs).

## 🛠 Features (In Progress Phase 1)
- Secure, private Telegram Bot (only responds to authorized specific User IDs)
- Dynamic LLM Routing (Switch between GPT-4, Claude 3, and Llama simply by configuring the `.env`)

## 🚀 How to Run this on AWS via GitHub

### 1. Set up on your Local Machine (Your Laptop)
1. Ensure you have Python 3 installed.
2. Clone this repository to your laptop.
3. Open a terminal in the folder and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
5. Rename `.env.example` to `.env`.
6. Get your API Keys:
   - **Telegram:** Talk to [@BotFather](https://t.me/BotFather) on Telegram and create a new bot to get your token.
   - **Allowed User ID:** Send a message to [@userinfobot](https://t.me/userinfobot) to get your numerical Telegram ID and paste it into the `.env` file for `ALLOWED_USER_IDS`.
   - **AI Keys:** Add whatever API keys you want to use (OpenAI, Anthropic, or Groq for free Llama access).

### 2. Push to GitHub
1. Create a new repository on your GitHub (Private is recommended to keep your custom logic safe).
2. Commit your code and push it up.
**(NEVER commit your `.env` file! It is ignored by default in good setups, but be careful not to push your pure API keys.)**

### 3. Deploy to AWS Instance
1. SSH into your AWS EC2 instance.
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/TelegramAssistant
   ```
3. Move into the directory and create the `.env` file on the server:
   ```bash
   cd TelegramAssistant
   nano .env
   ```
4. Paste the contents of your populated `.env` file into this server file, and save.
5. Install python venv and run it (Assume Ubuntu/Debian server):
   ```bash
   sudo apt update
   sudo apt install -y python3-venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
6. Start the bot!
   ```bash
   python bot.py
   ```
*(You can use `screen` or `tmux` or set it up as a systemd service to keep it running forever in the background!)*
