# epicbot
A Discord bot that interfaces with Reddit.

**Made by Team 10, section 002**

## Reaction Usage
:page_with_curl: - display post's summary

:page_facing_up: - display post's body

:bust_in_silhouette: - display post's author profile

:speech_balloon: - dispay post's comments

## Command Usage

### Help Commands

Shows this message. 
Individual Command(s) can be specified to filter the unspecified command(s).

!help

!help [command 1] [command 2] [command ...]

### Autofeed Commands

Requires at least 1 subreddit. Automatically post new submissions as they are posted to reddit.

![auto | feed | autofeed] [subreddit 1] [subreddit 2] [subreddit ...]

### Subreddit Commands

Requires a number. Post up to 10 posts based on your sort preference.

![hot | top | new | rising][1-10] [subreddit]

### Search Commands

Requires a number and search terms. Post up to 10 posts filtered by your search terms. 
Arguments with the '-' prefix are optional. Defaults to r/all.

!search[1-10] [search terms] -[relevance | top | new | comments] -[all | hour | day | week | month | year] -[subreddit]

### User Commands

Search for a user's profile.

!user [reddit username]

### Prefix Commands
Change EpicBot's prefix If no prefix is provided then it will reset to the default. Default is !

[current prefix]prefix [new prefix or nothing to reset to !]

### Examples

!auto memes dankmemes MemeEconomy

!top5 pics

!search5 Covid-19 -worldnews -top -alltime

!user Holofan4life

!prefix ~

!help auto prefix