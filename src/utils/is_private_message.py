import discord

async def is_private_message(message: discord.Message) -> bool:
    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(
            f"Hey <@{message.author.id}>, I'm a bot to play The Resistance Game.\n"
            "Use the /command command to see all commands available."
        )
        return True
    return False
