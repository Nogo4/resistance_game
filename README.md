# The Resistance Discord Bot

A Discord bot implementation of the popular social deduction game "The Resistance" where players work together to complete missions while hidden spies try to sabotage them.

## Table of Contents

- [Game Overview](#game-overview)
- [Features](#features)
- [Setup](#setup)
- [How to Play](#how-to-play)
- [Commands](#commands)
- [Game Rules](#game-rules)
- [File Structure](#file-structure)
- [Contributing](#contributing)

## Game Overview

The Resistance is a social deduction game for 5-10 players. Players are secretly assigned roles as either **Resistance members** or **Spies**. The Resistance must complete three missions successfully, while the Spies try to sabotage them by failing missions. The game is won when either the Resistance completes 3 missions or the Spies fail 3 missions.

## Features

- **Automatic game setup** with role assignment
- **Private game channels** created for each game
- **Interactive voting system** using Discord reactions
- **Mission progression** with varying team sizes
- **Role-based gameplay** with spy/resistance mechanics
- **Team leader rotation** system
- **Timed voting phases** for missions

## Setup

### Prerequisites

- Python 3.7+
- discord.py library
- A Discord bot token

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd resistance_game
   ```

2. Install required dependencies:
   ```bash
   pip install discord.py
   ```

3. Create a `token.txt` file in the root directory and add your Discord bot token:
   ```
   YOUR_DISCORD_BOT_TOKEN_HERE
   ```

4. Run the bot:
   ```bash
   ./start_bot.sh
   ```
   Or directly with Python:
   ```bash
   python3 ./src/main.py
   ```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `token.txt` file
4. Invite the bot to your server with the following permissions:
   - Send Messages
   - Use Slash Commands
   - Manage Channels
   - Add Reactions
   - Read Message History

## How to Play

### Starting a Game

1. Use the command `!play_resistance` in any text channel
2. Players have 10 seconds to react with 👍 to join the game
3. The bot will create a private channel for the game participants
4. Roles are automatically assigned (Resistance members and Spies)

### Game Flow

1. **Team Selection**: The team leader proposes a team for the mission
2. **Team Voting**: All players vote to approve or reject the proposed team
3. **Mission Execution**: If approved, selected players vote on the mission outcome
4. **Results**: Mission succeeds or fails based on votes
5. **Next Round**: Process repeats with a new team leader

## Commands

### Slash Commands

- `/propose_team <@player1> <@player2> ...` - **(Team Leader Only)** Propose a team for the current mission
- `/vote_mission <success|fail>` - **(Mission Members Only)** Vote on the mission outcome
- `/role` - Check your assigned role (Spy or Resistance)

### Text Commands

- `!play_resistance` - Start a new game in the current channel

## Game Rules

### Player Count & Spy Distribution

| Players | Spies | Resistance |
|---------|-------|------------|
| 5       | 2     | 3          |
| 6       | 2     | 4          |
| 7       | 3     | 4          |
| 8       | 3     | 5          |
| 9       | 3     | 6          |
| 10      | 4     | 6          |

### Mission Team Sizes

| Players | Round 1 | Round 2 | Round 3 | Round 4 | Round 5 |
|---------|---------|---------|---------|---------|---------|
| 5       | 2       | 3       | 2       | 3       | 3       |
| 6       | 2       | 3       | 4       | 3       | 4       |
| 7       | 2       | 3       | 3       | 4       | 4       |
| 8       | 3       | 4       | 4       | 5       | 5       |
| 9       | 3       | 4       | 4       | 5       | 5       |
| 10      | 3       | 4       | 4       | 5       | 5       |

### Special Rules

- **Round 4** (for 7+ players): Requires **2 fails** to fail the mission
- **Team Rejection**: If 5 teams are rejected in a row, the Spies automatically win
- **Mission Voting**: Players have 15 seconds to vote on missions
- **Resistance Restriction**: Resistance members can only vote "success" on missions
- **Spy Strategy**: Spies can vote either "success" or "fail" on missions

### Victory Conditions

- **Resistance Wins**: Complete 3 missions successfully
- **Spies Win**: Fail 3 missions OR cause 5 team rejections in a row

## File Structure

```
resistance_game/
├── src/
│   ├── main.py                 # Main bot file with Discord commands
│   ├── game/
│   │   ├── __init__.py        # Game module exports
│   │   ├── current_data.py    # Global game state storage
│   │   ├── get_mission_ctx.py # Mission context and rules
│   │   ├── mission.py         # Mission class implementation
│   │   ├── player.py          # Player class implementation
│   │   └── roles.py           # Role definitions
│   └── utils/
│       ├── __init__.py        # Utility module exports
│       ├── create_poll.py     # Discord poll creation
│       ├── get_token.py       # Token file reading
│       ├── get_user_ig.py     # Player lookup utilities
│       └── is_private_message.py # Message type checking
├── start_bot.sh              # Bot startup script
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Known Issues

- Games are stored in memory and will be lost if the bot restarts
- No persistence for ongoing games
- Limited error handling for edge cases

## Future Enhancements

- [ ] Database integration for game persistence
- [ ] Spectator mode
- [ ] Game statistics and leaderboards
- [ ] Custom game settings (timer duration, player limits)
- [ ] Better error handling and user feedback
- [ ] Game replay system

## License

This project is licensed under CC BY-NC 4.0
