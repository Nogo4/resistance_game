import asyncio
import discord

async def create_poll(channel, message):
    message += ("\nYou have 30 seconds to vote")
    poll_message = await channel.send(message)

    await poll_message.add_reaction("✅")
    await poll_message.add_reaction("❌")
    await asyncio.sleep(30)

    poll_message = await channel.fetch_message(poll_message.id)
    nb_check = -1
    nb_cross = -1
    for reaction in poll_message.reactions:
        if str(reaction.emoji) == "✅":
            nb_check += reaction.count
        elif str(reaction.emoji) == "❌":
            nb_cross += reaction.count
    return [nb_check, nb_cross]
