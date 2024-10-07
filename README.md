# RSS Bot

A simple bot that fetches RSS feeds and posts them to a Discord channel.

It keeps track of the last post it fetched, so it won't post the same post twice.

## Installation

1. Clone the repository
2. Install python version 3.11
3. Install the dependencies with `pip install -r requirements.txt`
4. Copy the `.env.example` file to `.env` and fill in the required values
5. Run the bot with `python main.py`

## Configuration

- The bot expects a list of names and urls in the `feeds.csv` file.
- For each feed, the bot will fetch the latest post and post it to the Discord channel.
