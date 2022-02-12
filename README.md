# MoodleTelegramBot
A bot made in Python that watches courses on a Moodle website for changes and notifies using a Telegram bot.

## Setup
1. Clone this repository and open it in your terminal.
2. Install the required pip packages with: `pip install -r requirements.txt`. You may use a virtualenv.
3. Proceed to configuration.

## Configuration
Rename `config.rename_to_json` to `config.json`.

### Explaining `config.json`:
- `username_whitelist`: A list of whitelisted usernames, without the starting '@'.
- `notify`: A list of usernames to be notified when changes are detected.
- `check_delay`: An integer, the check interval in seconds.
- `telegram_bot_token`: The Telegram Bot Token.
- `username_chat_id_cache`: Path for a small file that will be created as a cache for chat ids.
- `database`: Path for the sqlite3 database that will keep track of past and new Moodle entries.
- `base_url`: The base URL for your Moodle website. MUST END WITH '/'!
- `login`: The Moodle login.
- `password`: The Moodle password.
- `courses`: A list of courses that will be monitored:

#### Each course entry must contain:
- `id`: The course id, you can find it at the course URL. If the url ends with `course/view.php?id=1111`, the id is `1111`.
- `name`: The couse name, used for display only, you can set this to anything you like.
- `parser`: The parser to be used for that course. Must be `all`, `older`, `new`, `section` or `older and section`. Finding the right one is, most of the time, testing all of them. You may also implement your own at UrlScrapper and ParserTypes.
