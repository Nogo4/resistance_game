import discord
import asyncio
import random
import math
from utils import get_token, is_private_message, get_user_ig
from game import Player, RoleList, get_mission_ctx, current_games, current_players
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class GameStatus:
    WAITING_FOR_PLAYERS = 1
    IN_PROGRESS = 2
    FINISHED = 3

class Game:
    def __init__(self):
        self.creator = None
        self.players = []
        self.status = GameStatus.WAITING_FOR_PLAYERS
        self.round = 1
        self.nb_fails = 0
        self.nb_success = 0
        self.current_leader = 0
        self.channel = None
        self.team_vote_moment = False
        self.waiting_vote = False
        self.mission_vote_moment = False
        self.nb_player_on_mission = 0
        self.need_two_fails_on_mission = False
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
        await self.channel.send(message)
        self.status = GameStatus.IN_PROGRESS
        await self.game_in_progress()

    def end_of_round(self):
        self.players[self.current_leader].is_team_leader = False
        self.team_vote_moment = False
        self.waiting_vote = False
        self.mission_vote_moment = False

    async def procede_round(self):
        mission_ctx = get_mission_ctx(len(self.players), self.round, self.players, self.current_leader)
        self.nb_player_on_mission = mission_ctx[0]
        self.need_two_fails_on_mission = mission_ctx[1]
        self.current_leader = mission_ctx[2]
        self.players[self.current_leader].is_team_leader = True
        team_leader = self.players[self.current_leader]
        message = f"Round {self.round}:\nThe Team leader is <@{team_leader.user_id}>\nThe Team leader must create a team of {self.nb_player_on_mission} members.\n"

        if self.need_two_fails_on_mission:
            message += "Two fails are needed on this mission for spys :detective:.\n"
        else:
            message += "One fail is needed on this mission for spys :detective:.\n"
        await self.channel.send(message)
        self.team_vote_moment = True
        self.waiting_vote = True
        self.end_of_round()

    async def game_in_progress(self):
        self.init_roles()
        while self.round <= 5 and self.nb_fails < 3 and self.nb_success < 3:
            await self.procede_round()
            self.round += 1

    def init_roles(self):
        nb_spy = math.ceil(len(self.players) / 3)
        for spy in range(nb_spy):
            player = random.choice(self.players)
            player.role = RoleList.SPY

@bot.tree.command(name="role")
async def role_command(interaction: discord.Interaction):
    user_ig = get_user_ig(interaction.user.id)
    if user_ig is None:
        await interaction.response.send_message("You are not playing", ephemeral=True)
        return
    user_role = user_ig.role
    if user_role == RoleList.SPY:
        message = "You are a Spy :detective:"
    else:
        message = "You are a Resistant :shield:"
    await interaction.response.send_message(message, ephemeral=True)

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

@bot.event
async def on_ready():
    await bot.tree.sync()

if __name__ == "__main__":
    token = get_token("token.txt")

    if token is None:
        print("Token not found. Please create a token.txt file with your bot token.")
        exit(1)
    bot.run(token)
