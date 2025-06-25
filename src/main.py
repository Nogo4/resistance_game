import discord
import asyncio
from utils import get_token, is_private_message
from game import Player, RoleList
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
current_games = []
current_players = []

class GameStatus:
    WAITING_FOR_PLAYERS = 1
    IN_PROGRESS = 2
    FINISHED = 3

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
        creator_name = guild.get_member(self.creator).name
        self.channel = await guild.create_text_channel("resistance-game-" + str(creator_name), overwrites=overwrites)
        self.message = await self.channel.send(message)
        self.status = GameStatus.IN_PROGRESS

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
                await new_game.init_game()
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
