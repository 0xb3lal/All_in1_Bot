# Balance Telegram Bot

A Telegram bot that helps manage and generate balanced query distributions with an interactive conversation flow.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![python-telegram-bot](https://img.shields.io/badge/PTB-20.6-blue.svg)

## Features

- 🚀 Interactive button-based interface
- 💰 Balance checking functionality
- ⚡ Query generation with size distribution
- 📝 Session-based conversation handling
- 🎯 User-friendly typing indicators
- ⚠️ Error handling and graceful fallbacks

## Commands

- `/start` - Initialize the bot and show main menu
- `/about` - Show bot information and author contact
- `/genquery` - Start query generation conversation
- `/cancel` - Cancel current operation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/0xb3lal/Balance.git
cd Balance
```

2. Create a virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the bot:
- Create a `config.py` file with your bot token:
```python
TOKEN = "your_bot_token_here"
```

5. Run the bot:
```bash
python main.py
```

## Docker

You can run the bot inside Docker which makes it easy to deploy or run on another machine.

Build the image from the project root:

```powershell
docker build -t balance-bot:latest .
```

Run the container (provide your bot token and optional CHAT_ID):

```powershell
docker run -e TOKEN="<your_token>" -e CHAT_ID="<optional_chat_id>" --name balance-bot balance-bot:latest
```

Notes about the Docker image:
- The image contains an entrypoint script `docker-entrypoint.sh`. If `/app/config.py` is not present inside the image, the entrypoint will generate `config.py` from the `TOKEN` and optional `CHAT_ID` environment variables.
- You can mount your own `config.py` instead of using environment variables:

```powershell
docker run -v C:\path\to\config.py:/app/config.py -e TOKEN="..." balance-bot:latest
```

### docker-compose example

Here is an example `docker-compose.yml` you can use for local/dev runs:

```yaml
version: '3.8'
services:
   balance-bot:
      build: .
      environment:
         - TOKEN=${TOKEN}
         - CHAT_ID=${CHAT_ID}
      restart: unless-stopped
      container_name: balance-bot
```

Make sure to set `TOKEN` (and optionally `CHAT_ID`) in an `.env` file or export them before running `docker-compose up`.


## Usage

1. **Start the Bot**
   - Send `/start` to get the main menu
   - Use inline buttons for navigation

2. **Check Balance**
   - Click the "Balance" button
   - View available traffic information

3. **Generate Queries**
   - Click "Gen Query" or use `/genquery`
   - Follow the interactive prompts:
     1. Enter session IDs (comma or space-separated)
     2. Specify desired total size (e.g., "2.1GB" or "500MB")
   - Get balanced SQL queries as result

## Project Structure

```
Balance/
├── main.py           # Bot initialization and handler setup
├── handler.py        # Command and conversation handlers
├── config.py         # Configuration and bot token
├── genquery.py       # Query generation logic
├── core/
│   ├── __init__.py
│   ├── bot_init.py   # Bot instance initialization
│   └── data_loader.py# Data loading utilities
└── requirements.txt  # Project dependencies
```

## Dependencies

- python-telegram-bot==20.6
- (other dependencies from requirements.txt)

## Running in Docker vs Local Python

- Local Python: edit or provide `config.py` and run `python main.py`.
- Docker: prefer to pass `TOKEN` via environment variables or mount a `config.py` into `/app/config.py`.

## Error Handling

- Network timeouts
- Invalid inputs
- Conversation state management
- Graceful error messages

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## Author

- [@0xb3lal](https://github.com/0xb3lal)
- Contact: [@belalammar](https://t.me/belalammar)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Special thanks to contributors and users