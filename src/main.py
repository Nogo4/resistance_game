import discord
import asyncio
from discord.ext import commands
from utils.get_token import read_token_file as get_token

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
current_games = []
current_players = []

class RoleList:
    SPY = "Spy"
    RESISTANT = "Resistant"

class GameStatus:
    WAITING_FOR_PLAYERS = 1
    IN_PROGRESS = 2
    FINISHED = 3

class Player:
    def __init__(self, user_id):
        self.user_id = user_id

class Game:
    def __init__(self):
        self.creator = None
        self.players = []
        self.status = GameStatus.WAITING_FOR_PLAYERS
        self.round = 0
        self.guild = None

    async def add_player(self, user_id):
        if user_id in current_players:
            user = await bot.fetch_user(user_id)
            await user.send(
                "You are already in a game, please wait for it to finish before joining another."
            )
            return False
        if user_id not in [p.user_id for p in self.players]:
            self.players.append(Player(user_id))
            current_players.append(user_id)
            return True
        return False
    async def init_game(self):
        guild = self.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        for player in self.players:
            user = guild.get_member(player.user_id)
            if user:
                overwrites[user] = discord.PermissionOverwrite(view_channel=True)
        message = "Welcome to The Resistance Game!\n"
        for player in self.players:
            user = guild.get_member(player.user_id)
            if user:
                message += f"- <@{user.id}>\n"
        self.channel = await guild.create_text_channel("resistance-game" + str(self.creator), overwrites=overwrites)
        self.message = await self.channel.send(message)

async def is_private_message(message: discord.Message) -> bool:
    if isinstance(message.channel, discord.DMChannel):
        if message.content == "!help":
            await message.channel.send(
                "This bot is in development, please wait for the next update."
            )
            return True
        else:
            await message.channel.send(
                f"Hey <@{message.author.id}>, I'm a bot to play The Resistance Game.\n"
                "Use the !help command in private messages to see how to play."
            )
        return True
    return False

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if await is_private_message(message):
        return
    await bot.process_commands(message)

@bot.command()
async def play_resistance(ctx):
    message = await ctx.send(
        "Hey <@" + str(ctx.author.id) + ">'s game will start soon, all players who want to play have to react with 👍 to join the game\n"
        "You have 10 seconds to react."
    )
    await message.add_reaction("👍")
    await asyncio.sleep(10)

    message = await ctx.channel.fetch_message(message.id)
    new_game = Game()
    new_game.creator = ctx.author.id
    for reaction in message.reactions:
        if str(reaction.emoji) == "👍":
            users = [user async for user in reaction.users()]

            for user in users:
                if not user.bot:
                    await new_game.add_player(user.id)
            if new_game.players:
                message = f"🗳️Players list : \n"
                for player in new_game.players:
                    message += f"- <@{player.user_id}>\n"
                await ctx.send(message)
                new_game.guild = ctx.guild
                current_games.append(new_game)
            else:
                await ctx.send("❌ Nobody want play.")
            return

    await ctx.send("❌ La réaction 👍 n'a pas été trouvée.")


if __name__ == "__main__":
    token = get_token("token.txt")
    if token is None:
        print("Token not found. Please create a token.txt file with your bot token.")
        exit(1)
    bot.run(token)
