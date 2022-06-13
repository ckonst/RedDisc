# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.2.4]
Updated Help Menu, Style, and formatting.

### Added
- Unit Tests that actually test the code.
- Typehints, and some more comments.
- requirements.txt

## [1.2.3]
A few bugfixes, test script
###

### Added
- Automated test script with test.py and tests.txt
- !help command now shows example usage for specific commands
### Changed
- autofeed now sleeps for 1 millisecond instead of 10 seconds, to speed up response times
### Fixed
- url_morph now checks for multiple image extensions with imgur url
- No longer removes reactions that are not used for changing the displayed information


## [1.2.2]
- Fixed comment embeds to only include "..." when length of the comment is greater than 100 chars

## [1.2.1]
- Now creates prefixes.json if it doesn't exist

## [1.2.0]
Added custom prefixes
### Added
- !prefix [new prefix] command to support per server custom prefixes
    - every server's prefix is stored in prefix.json
    - if no new prefix is specified it revert to the default: *!*
- !help and !help prefix now display relevent prefix info

## [1.1.0]
Added autofeed command, updated help command
### Added
- !auto [subreddit] command:
    - When toggled on, the bot will post new submissions from a given subreddit in real time
    - Call a second time to toggle off (no other arguments needed)
    - Will post the feed to the channel this was invoked in

### Changed
- autofeed now appears in the help menu
- !help [command] to post helpful information about a single command
- updated readme

## [1.0.3]
Modified !help command
### Added
- Custom !help command
- create_help_embed function for the help command
- Documentation for the above

### Changed
- !help command now displays command usage syntax

## [1.0.2]
Updated user embeds
### Changed
- User embed color to differentiate it from posts

### Fixed
- A bug when displaying a nonexistent user

## [1.0.1]
Style and Documentation update
### Added
- Doc strings for all functions (that didn't already have one)
- Variables for repeated function calls
- New and/or upadted comments to various code blocks for clarity

### Changed
- Some doc strings for consciseness
- Actually updated the changelog

### Removed
- Unnecessary lines

## [1.0.0]
All basic functionality is now implemented
### Added
- Modify image url function for valid embedding
- Image extension function to determine if embed image is needed
- Embeds for the text body, comments, main submission, and user profile
- Added more info to user embeds
- Function for creating a user embed for deleted user
- Checking for suspended AND deleted users
- Suspended and deleted user checking
- Bot now reacts to its own posts with emojis
- on_raw_reaction_add function to handle user emoji reactions
- Editing of message embed content based on emoji reactions
- View user profiles with !user command
- search function for !post command
- search time filters

### Changed
- Initial url in embed to be full URL and made all adjustments needed
- Moved previous blocks of code to functions for readablity and modularity
 
### Removed
- URL field
- URL portion from user URL embed if called from !user

## [0.3.0] - 2020-09-22
Error checking, sorting, cleaner code, and updated documentation
### Added
- Better variable names
- cleaner code
- error checking for invalid or nonexistent subreddits and users
- sorting through command aliases
- main command name is now hot
- updated documentation

## [0.2.0] - 2020-09-05
Simplified the code, added more functionality to the main command.
### Added
- top command replaces the title command and posts the top x posts based on the number specified by the command invocation
- documentation
### Removed
- !hey command
- !title command
- !quit command

## [0.1.0] - 2020-09-05
### Added
- !hey command: on command, the bot will say hi, mentioning the author of the message
- !title command: the bot will post the top x titles of posts on reddit

## [0.0.0] - 2020-09-05
Initial commit, added the baseline bot code.
### Added
- main.py
- .gitignore
- added README.md
