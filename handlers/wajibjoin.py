from pyrogram import Client, filters

join_channels = {}

@Client.on_message(filters.command("setjoin"))
async def setjoin(client, message):
    if len(message.command) < 2:
        return await message.reply("Gunakan `/setjoin @channel1,@channel2`")
    chans = message.command[1].split(",")
    join_channels[message.from_user.id] = chans
    await message.reply(f"✅ Channel wajib join diset: {', '.join(chans)}")

@Client.on_message(filters.command("getjoin"))
async def getjoin(client, message):
    chans = join_channels.get(message.from_user.id)
    if not chans:
        return await message.reply("Belum ada channel wajib join.")
    await message.reply(f"📋 Channel wajib join kamu:\n" + "\n".join(chans))
