## Sheets Bot
This bot was designed for the [Spreadsheets Discord Community](https://discord.gg/M9GKpPd).
It is currently being hosted on a free tier Google Cloud compute instance.

### Features
- [x] Google Sheets and Excel Function lookup
- [x] Parroting commands
- [ ] [sheets.wiki] lookup

### Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

When you fork this repo, you'll need to make a venv and install the requirements:
```sh
python3 -m venv .
source bin/activate
pip install -r requirements.txt
```

You'll also need to create a .env file with the following contents:
```sh
key=YOUR_DISCORD_BOT_KEY
```

From there, you should be able to simply run `python3 bot.py` and the bot will start up.
