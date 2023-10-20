# Django Discord Bot
Allows for syncing rss feeds into discord forum channels as well as providing some useful moderation commands.

### Configuration
All base configuration parameters are set through an .env file (environment variables supersede them, if present).
Take a look at the example.env file for a template.

#### RSS-Feeds
The bot can sync from any rss feed into any discord forum channel (normal discord channels are not supported).

##### Note for adding new feeds
RSS feeds may return their content in slightly different ways, or use different formatting styles.
Because of this you might have to create a custom Converter function which takes in the raw HTML from the feed and converts it to something discord can display in a meaningful way.
This converter can then be configured to be used in the feeds.json file for the appropriate feed.

##### Setup feeds
Copy the feeds.json.example file from this repository and use it as a template.
Two RSS feeds are prefilled (The Django Forum and Django Chat).

The `destination_channel_id` denotes the id of the discord destination forum channel.

You can add as many feeds as you like, you might have to adjust the `RSS_SYNC_INTERVAL_SECONDS` setting to not have clashing synchronization processes.

### Setup
You can run the bot using docker.
There is also a docker-compose.yml included for making the setup simpler.

Just make sure that you mount your feeds.json in the container at `/app/feeds.json`.

When you first setup the bot you might have to synchronize the slash commands.
Run `-sync` (Replace the dash with your configured prefix), this may take up to a few minutes, the bot will respond when the sync is done.

### Contributing
If you'd like to contribute something to this bot, lets chat!
Just open up an issue.
If you want to contribute code, look at existing issues and submit a pull request.

### Attribution
The Gong-sound.mp3 audio file was sourced from https://orangefreesounds.com/gong-sound/.
