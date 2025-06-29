import discord
import asyncio
import random
import math
from utils import get_token, is_private_message, get_user_ig, create_poll
from game import Player, RoleList, get_mission_ctx, current_games, current_players
from game.mission import Mission
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
        self.nb_refused_teams = 0
        self.channel = None
        self.team_vote_moment = False
        self.waiting_vote = False
        self.mission_vote_moment = False
        self.nb_player_on_mission = 0
        self.mission = Mission()
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

    def end_of_round(self, reset_team_vote: bool):
        self.players[self.current_leader].is_team_leader = False
        self.team_vote_moment = False
        self.waiting_vote = False
        self.mission_vote_moment = False
        self.mission.players_list.clear()
        self.mission.result_list.clear()
        for player in self.players:
            player.vote_mission = False
        if reset_team_vote:
            self.nb_refused_teams = 0

    async def procede_round(self):
        mission_ctx = get_mission_ctx(len(self.players), self.round, self.players, self.current_leader)
        self.nb_player_on_mission = mission_ctx[0]
        self.need_two_fails_on_mission = mission_ctx[1]
        self.current_leader = mission_ctx[2]
        self.players[self.current_leader].teamleader = True
        team_leader = self.players[self.current_leader]
        message = f"Round {self.round}:\nThe Team leader is <@{team_leader.user_id}>\nThe Team leader must create a team of {self.nb_player_on_mission} members.\n"

        if self.need_two_fails_on_mission:
            message += "Two fails are needed on this mission for spys :detective:.\n"
        else:
            message += "One fail is needed on this mission for spys :detective:.\n"
        await self.channel.send(message)
        self.team_vote_moment = True
        self.waiting_vote = True
        while self.waiting_vote and self.nb_refused_teams < 5:
            await asyncio.sleep(1)
        if self.nb_refused_teams >= 5:
            self.end_of_round(False)
        self.waiting_vote = True
        self.mission_vote_moment = True
        mission_message = await self.channel.send("You have 15 seconds to vote for the mission.\nDo /vote_mission sucess or fail to vote.")
        for i in range(1, 16):
            await asyncio.sleep(1)
            await mission_message.edit(content=f"You have {15 - i} seconds to vote for the mission.\nDo /vote_mission sucess or fail to vote.")
        await mission_message.edit(content="The vote is now closed.")
        while len(self.mission.result_list) < len(self.mission.players_list):
            self.mission.result_list.append("success")
        nb_fail = self.mission.count_fail()
        if (self.need_two_fails_on_mission and nb_fail >= 2) or (not self.need_two_fails_on_mission and nb_fail >= 1):
            self.nb_fails += 1
            await self.channel.send(f"The mission has failed with {nb_fail} fails.")
        else:
            self.nb_success += 1
            await self.channel.send(f"The mission has succeeded ({nb_fail} fails.)")

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

def get_user_game(user_id):
    for game in current_games:
        for player in game.players:
            if player.user_id == user_id:
                return game
    return None

@bot.tree.command(name="propose_team")
async def propose_team_command(interaction: discord.Interaction, team: str):
    user_ig = get_user_ig(interaction.user.id)

    if user_ig is None:
        await interaction.response.send_message("You are not playing", ephemeral=True)
        return
    if not user_ig.teamleader:
        await interaction.response.send_message("You are not the team leader", ephemeral=True)
        return
    game = get_user_game(interaction.user.id)
    if game is None:
        await interaction.response.send_message("You are not in a game", ephemeral=True)
        return

    members = []
    for word in team.split():
        if word.startswith("<@") and word.endswith(">"):
            user_id = int(word.strip("<@!>"))
            member = interaction.guild.get_member(user_id)
            if member:
                members.append(member)

    if len(members) != game.nb_player_on_mission:
        await interaction.response.send_message(
            f"You must mention exactly {game.nb_player_on_mission} players.", ephemeral=True
        )
        return

    for member in members:
        if member.id not in [p.user_id for p in game.players]:
            await interaction.response.send_message(f"{member.mention} is not a player in this game", ephemeral=True)
            return

    message = "The team leader <@" + str(interaction.user.id) + "> proposes the team:\n"
    for member in members:
        message += f"- <@{member.id}>\n"

    await interaction.response.defer()
    vote_result = await create_poll(game.channel, message)
    await interaction.followup.send(f"The vote is now closed, you can check result in <#{game.channel.id}>.", ephemeral=True)
    if vote_result[0] > vote_result[1]:
        game.waiting_vote = False
        game.team_vote_moment = False
        game.mission_vote_moment = True
        await game.channel.send(f"The team has been accepted with {vote_result[0]} votes for and {vote_result[1]} against.")
        for member in members:
            member_ig = get_user_ig(member.id)
            game.mission.add_player(member_ig)
    else:
        game.nb_refused_teams += 1
        await game.channel.send(f"The team has been rejected with {vote_result[0]} votes for and {vote_result[1]} against.")

@bot.tree.command(name="vote_mission")
async def vote_mission_command(interaction: discord.Interaction, vote: str):
    user_ig = get_user_ig(interaction.user.id)

    if user_ig is None:
        await interaction.response.send_message("You are not playing 1", ephemeral=True)
        return
    game = get_user_game(interaction.user.id)
    if game is None:
        await interaction.response.send_message("You are not in a game 2", ephemeral=True)
        return
    if user_ig.user_id not in [p.user_id for p in game.mission.players_list]:
        await interaction.response.send_message("You are not in the mission", ephemeral=True)
        return
    if not user_ig.vote_mission:
        await interaction.response.send_message("You already vote for this mission", ephemeral=True)
        return
    vote_lower = vote.lower()
    if vote_lower.lower() not in ["success", "fail"]:
        await interaction.response.send_message("You must vote 'success' or 'fail'", ephemeral=True)
        return
    if vote_lower == "fail" and user_ig.role == RoleList.RESISTANT:
        await interaction.response.send_message("You cannot vote 'fail' as a Resistant", ephemeral=True)
        return
    game.mission.add_vote(user_ig, vote_lower)
    await interaction.response.send_message(f"You voted {vote_lower} for the mission.", ephemeral=True)

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
