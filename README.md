# RSS Bot

A simple bot that fetches RSS feeds and posts them to a Discord channel.

It keeps track of the last post it fetched, so it won't post the same post twice.

It ignores posts that have the text "THIS IS A SCHEDULED EVENT" in the title.

## Installation

1. Clone the repository
2. Install python version 3.11
3. Install the dependencies with `pip install -r requirements.txt`
4. Copy the `.env.example` file to `.env` and fill in the required values
5. Run the bot with `python main.py`

## Configuration

- The bot expects a list of names and urls in the `feeds.csv` file.
- For each feed, the bot will fetch the latest post and post it to the Discord channel.


## Deployment

1. Install docker
2. Build the docker image with `docker build -t rss-bot .`
3. Run the docker container with `docker run -d -v /some/path/data:/app/data --name rss-bot rss-bot`
> Note: The `-v /some/path/data:/app/data` flag is used to mount the data folder to the container. This is where the bot stores the last post it fetched for each feed. If you don't mount the data folder, the bot will lose track of the last post it fetched when the container is restarted.