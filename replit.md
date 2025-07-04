# Unreal Discord Bot

## Overview

Unreal is a comprehensive Arabic Discord bot designed for community management with features including voice activity rewards, verification system, moderation tools, games, music functionality, and announcements. The bot is built using Python with discord.py and SQLite for data persistence.

## System Architecture

### Backend Architecture
- **Framework**: Python with discord.py library
- **Database**: SQLite with aiosqlite for async operations
- **Configuration**: JSON-based configuration system
- **Architecture Pattern**: Cog-based modular design for Discord bots

### Data Storage
- **Primary Database**: SQLite (unreal_bot.db)
- **Configuration**: JSON file (config.json)
- **Data Access**: Async database operations using aiosqlite

### Authentication & Authorization
- **Discord Integration**: Uses Discord's OAuth2 through bot tokens
- **Role-based Permissions**: Admin and moderator role configurations
- **Verification System**: Reaction-based member verification

## Key Components

### Core Bot Framework
- **main.py**: Entry point with bot initialization and event handling
- **database.py**: Database abstraction layer with SQLite operations
- **config.json**: Centralized configuration management

### Feature Modules (Cogs)
1. **Voice Rewards** (`cogs/voice_rewards.py`)
   - Tracks voice channel activity
   - Awards XP based on time spent in voice channels
   - Automated role rewards based on voice activity levels

2. **Verification System** (`cogs/verification.py`)
   - Reaction-based member verification
   - Automated role assignment upon verification
   - Configurable verification messages in Arabic

3. **Moderation Tools** (`cogs/moderation.py`)
   - Member kick/ban functionality
   - Warning system with tracking
   - Automated moderation logging

4. **Games & Entertainment** (`cogs/games.py`)
   - Trivia questions with Arabic content
   - XP rewards for game participation
   - Multiple difficulty levels

5. **Announcements** (`cogs/announcements.py`)
   - Administrative announcement system
   - Channel-specific message broadcasting
   - Rich embed formatting

6. **Music System** (`cogs/music.py`)
   - Queue-based music playback
   - Playlist support
   - Duration and queue length limits

### Utility Components
- **arabic_responses.py**: Localized Arabic messages and responses
- **helpers.py**: Common utility functions for time formatting and parsing

## Data Flow

### Voice Activity Tracking
1. Bot monitors voice state changes
2. Records join/leave times in voice_activity table
3. Calculates XP based on duration and channel bonuses
4. Updates user totals and assigns reward roles

### User Verification
1. Admin sets up verification channel and role
2. Bot posts verification message with reaction
3. Users react to verify themselves
4. Bot assigns verified role automatically

### Game Interactions
1. Users initiate games through commands
2. Bot presents questions/challenges
3. Responses are evaluated and XP awarded
4. Results stored in user statistics

## External Dependencies

### Required Python Packages
- `discord.py`: Discord API wrapper
- `aiosqlite`: Async SQLite operations
- `asyncio`: Asynchronous programming support

### Discord Permissions Required
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Connect to Voice Channels
- Manage Roles
- Kick Members
- Ban Members
- Add Reactions

## Deployment Strategy

### Environment Setup
- Python 3.8+ runtime environment
- SQLite database file creation on first run
- Bot token configuration through environment variables or secure storage

### Configuration Management
- JSON-based configuration for easy customization
- Runtime configuration updates for certain features
- Database schema auto-initialization

### Scalability Considerations
- SQLite suitable for single-server deployments
- Modular cog system allows feature expansion
- Async operations prevent blocking

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 01, 2025. Initial setup