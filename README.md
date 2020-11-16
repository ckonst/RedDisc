# epicbot
A Discord bot that interfaces with Reddit.

**Made by Team 10, section 002**

## Reaction Usage
:page_with_curl: - display post's summary

:page_facing_up: - display post's body

:bust_in_silhouette: - display post's author profile

:speech_balloon: - dispay post's comments

## Command Usage

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

### Examples

!auto memes dankmemes MemeEconomy

!top5 pics

!search5 Covid-19 -worldnews -top -alltime

!user gallowboob