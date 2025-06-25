import discord

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
