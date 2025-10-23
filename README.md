# Balance Bot

[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://t.me/MyBot) [![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)](https://www.python.org/)

Balance is a compact Telegram bot that transforms a list of session identifiers and a requested total data size into SQL UPDATE statements. It divides the total bytes across the provided sessions in a randomized but balanced way and returns ready-to-run SQL suitable for updating per-session accounting records.

Inputs
- A list of session IDs (space- or comma-separated)
- A total size (human-readable, e.g. "2.1GB" or "500MB")

Output
- SQL UPDATE statements assigning acctinputoctets and acctoutputoctets per session; allocations sum to the requested total.

Behavior notes
- Designed for testing and controlled simulations. The bot validates basic inputs and supports cancelling an in-progress operation.
- Keep the bot token and any configuration private.

If you want a shorter or more technical description (or an example), tell me and I will update it.
