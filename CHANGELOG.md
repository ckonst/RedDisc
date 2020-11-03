# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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
