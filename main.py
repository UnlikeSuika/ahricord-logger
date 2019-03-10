import discord
import json

release_ver = False
client = discord.Client(max_messages=10000)
mail_json_path = "mails.json"
mail_data = None

if release_ver:
    with open("token_release.txt", "r") as token_file:
        token = token_file.read().split('\n')[0]
    channel_in = "368797408479412226" # ahricord main
    channel_out = "418062533732335626" # logger channel
else:
    with open("token_test.txt", "r") as token_file:
        token = token_file.read().split('\n')[0]
    channel_in = "483529593089687552" # UnlikeServer spam channel
    channel_out = "228160636742402058" # another spam channel
    channel_mail = "228160636742402058"


@client.event
async def on_ready():
    print("Name: " + client.user.name)
    print("ID: " + client.user.id)
    channels = client.get_all_channels()
    for channel in channels:
        print("--------------")
        print("Server name: {}".format(channel.server.name))
        print("Channel name: {}".format(channel.name))
        print("Channel ID: {}".format(channel.id))
    get_mail_log()


@client.event
async def on_message(message):
    if not message.channel == client.get_channel(channel_in):
        if str(type(message.channel)) == "<class 'discord.channel.PrivateChannel'>" and \
                message.content.split()[0] == "!mail":
            await process_mail(message)
        return
    ctn = "**========== Message received ==========**\n"
    ctn += get_info(message)
    await client.send_message(client.get_channel(channel_out), content=ctn)


@client.event
async def on_message_delete(message):
    if not message.channel == client.get_channel(channel_in):
        return
    ctn = "**========== Message deleted ==========**\n"
    ctn += get_info(message)
    await client.send_message(client.get_channel(channel_out), content=ctn)


@client.event
async def on_message_edit(before, after):
    if not before.channel == client.get_channel(channel_in):
        return
    ctn = "**========== Message edited ==========**\n"
    ctn += "**BEFORE**\n"
    ctn += get_info(before)
    ctn += "**AFTER**\n"
    ctn += "__Edited time__: {}\n".format(str(after.edited_timestamp))
    ctn += get_info(after)
    await client.send_message(client.get_channel(channel_out), content=ctn)


def get_info(message):
    ctn = "__Time__: {}\n".format(str(message.timestamp))
    ctn += "__Author name__: {}\n".format(message.author.name)
    ctn += "__Author ID__: {}\n".format(message.author.id)
    try:
        ctn += "__Content__: {}\n".format(message.clean_content)
    except:
        ctn += "No message content.\n"
    ctn += "__Message ID__: {}\n".format(message.id)
    return ctn


# TODO: saving log of mails, adding report functionality
async def process_mail(message):
    global mail_data
    # assume that the content string starts with "!mail"
    ctn = "**========== New mail ==========**\n"
    ctn += "__Message ID__: {}\n".format(message.author.id)
    ctn += "__Content__: {}\n".format(message.content[5:].strip())
    mail_data[message.id] = (message.author.id, message.content[5:].strip())
    write_mail_log()
    await client.send_message(client.get_channel(channel_mail), content=ctn)


def get_mail_log():
    global mail_data, mail_json_path
    try:
        with open(mail_json_path, "r") as mail_json_file:
            mail_data = json.load(mail_json_file)
    except:
        mail_data = {}


def write_mail_log():
    global mail_data, mail_json_path
    with open(mail_json_path, 'w') as mail_json_file:
        json.dump(mail_data, mail_json_file)


client.run(token)
