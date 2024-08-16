# Telegram Bot with Google Sheets integration

this is a Telegram bot that integrates with Google Sheets to log user inputs
the bot allows users to add data, clear the cache, and select various categories for tracking expenses and incomes

## features

- **command `/start`:** start interaction with the bot.
- **command `/add`:** begin the process of adding a new entry.
- **command `/clear`:** clear the current session's data.
- **currency Selection:** users can choose between USD and RUB.
- **type Selection:** users can select whether the entry is for "spends" or "incomes".
- **сategory Selection:** based on the selected type, users can choose the appropriate category.
- **amount & description:** users can provide an amount and an optional description for the entry.
- **Google Sheets integration:** the bot automatically logs the user's input to a Google Sheet.