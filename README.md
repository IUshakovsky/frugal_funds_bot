# Frugal Funds - Personal Expense Tracking Telegram Bot

Frugal Funds is a Telegram bot designed to help users track their personal expenses efficiently. It utilizes MongoDB for data storage and is built using Python and aiogram library.

## Features

- **Expense Tracking**: Easily track your daily expenses by sending messages to the Frugal Funds bot on Telegram.
- **Expense Categories**: Categorize your expenses to get a better understanding of where your money is going.
- **Detailed Reports**: Generate reports by different periods to explore your spending habits over time.
- **User ids whitelist**: Set users of your bot. Others will be ignored.
## Setup

To set up the Frugal Funds bot, follow these steps:

```bash
# Clone the Repository
git clone https://github.com/IUshakovsky/frugal_funds_bot.git
cd frugal_funds_bot

# Optionally create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Create '.env' configuration file
touch .env

# Set up MongoDB
# Make sure you have MongoDB installed and running on your system.
# Update the MongoDB connection details in '.env' file:
# MONGO_URI = mongodb://127.0.0.1:27017
# DB = expenses

# Telegram bot setup
# Create a new bot on Telegram using BotFather.
# Obtain the bot token and update the '.env' file with your bot token:
# BOT_TOKEN = [YOUR TOKEN]

# Set allowed users for the bot in '.env':
# ALLOWED_USERS = [user_id1, ...]

# Run the Bot
python3 ffunds_bot.py
```

## Usage

Once the bot is up and running, you can interact with it directly through Telegram with commands: 

- /add: Add new expense record.
- /new_cat: Add new categroy
- /delete_cat: Delete existing category
- /get_stat: Get reports 
- /quick_stat: Get current month's total expenses


## Contributing
Contributions are welcome! If you'd like to contribute to the development of Frugal Funds, please follow these guidelines:

- Fork the repository and create your branch from main.
- Make your changes.
- Test your changes thoroughly.
- Create a pull request with a detailed description of your changes.


## License
This project is licensed under the MIT License - see the LICENSE file for details.