import discord
import json
import datetime

release_ver = False
client = discord.Client(max_messages=10000)
mail_json_path = "mails.json"
mail_data = {}
report_list_path = "reported.txt"
reported_user_list = []
log = None
log_path = "log.txt"

if release_ver:
    with open("token_release.txt", "r") as token_file:
        token = token_file.read().strip()
    channel_in = "368797408479412226" # ahricord main
    channel_out = "418062533732335626" # logger channel
    channel_mail = "554273414991314955"
else:
    with open("token_test.txt", "r") as token_file:
        token = token_file.read().strip()
    channel_in = "483529593089687552" # UnlikeServer spam channel
    channel_out = "262089968950706188" # another spam channel
    channel_mail = "228160636742402058" #"434757762707095554"


@client.event
async def on_ready():
    print("Name: " + client.user.name)
    print("ID: " + client.user.id)
    channels = client.get_all_channels()
    open_log()
    ctn = "========== {0} ==========\n".format(str(datetime.datetime.now()))
    ctn += "Bot is now booting up.\n"
    for channel in channels:
        ctn += "--------------\n"
        ctn += "Server name: {}\n".format(channel.server.name)
        ctn += "Channel name: {}\n".format(channel.name)
        ctn += "Channel ID: {}\n".format(channel.id)
    print(ctn)
    write_log(ctn)
    close_log()
    get_mail_log()
    get_reported_users_list()


@client.event
async def on_message(message):
    global channel_out
    if not (message.channel.id == channel_out):
        open_log()
        ctn = "----- on_message -----\n"
        ctn += "timestamp: {0}\n".format(str(message.timestamp))
        ctn += "author name: {0}\n".format(message.author.name)
        ctn += "author ID: {0}\n".format(message.author.id)
        ctn += "content: {0}\n".format(message.content)
        ctn += "server: {0}\n".format(str(message.server))
        ctn += "channel: {0}\n".format(str(message.channel))
        write_log(ctn)
        close_log()
    if not message.channel == client.get_channel(channel_in):
        if str(type(message.channel)) == "<class 'discord.channel.PrivateChannel'>" and \
                message.content.split()[0] == "!mail":
            await process_mail(message)
        elif message.channel.id == channel_mail and message.content.split()[0] == "!report":
            await report(message)
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


async def process_mail(message):
    global mail_data, reported_user_list
    if message.author.id in reported_user_list:
        ctn = "You have been reported. You cannot send any more suggestions.\n"
        # assumes that message is within PrivateChannel
        await client.send_message(message.channel, content=ctn)
        return
    # assume that the content string starts with "!mail"
    ctn = "**========== New mail ==========**\n"
    ctn += "__Message ID__: {}\n".format(message.id)
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
    with open(mail_json_path, "w") as mail_json_file:
        json.dump(mail_data, mail_json_file)


def get_reported_users_list():
    global reported_user_list, report_list_path
    reported_user_list = []
    try:
        with open(report_list_path, "r") as report_file:
            for line in report_file.readlines():
                reported_user_list.append(line.strip())
    except:
        pass


async def report(message):
    global mail_data, reported_user_list, report_list_path
    report_id = message.content[7:].strip()
    try:
        add_id = mail_data[report_id][0]
    except:
        ctn = "Message ID not found.\n"
        await client.send_message(client.get_channel(channel_mail), content=ctn)
        return
    if add_id in reported_user_list:
        ctn = "This user has already been reported.\n"
        await client.send_message(client.get_channel(channel_mail), content=ctn)
        return
    reported_user_list.append(add_id)
    with open(report_list_path, "a") as report_file:
        report_file.write(add_id + "\n")
    ctn = "**========== Mail Reported ==========**\n"
    ctn += "__Message ID__: {}\n".format(add_id)
    ctn += "__Content__: {}\n".format(mail_data[report_id][1])
    await client.send_message(client.get_channel(channel_mail), content=ctn)


def open_log():
    global log, log_path
    if (log is None) or log.closed:
        log = open(log_path, "a")


def close_log():
    global log
    if (not log is None) and (not log.closed):
        log.close()


def write_log(content):
    global log
    log.write(content + "\n")


client.run(token)
