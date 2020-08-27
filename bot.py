import os  # for importing env vars for the bot to use
from twitchio.ext import commands
from pprint import pprint
from datetime import datetime

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)

# Bots so logs don't get cluttered

bots = [
    'nightbot',
    'streamelements'
]

# Available queue commands
queueCommands = [
    "join",
    "leave",
    "clear",
    "status",
    "list",
    "create",
    "remove",
    "reset",
    "close",
    "open",
    "next",
    "undonext",
    "repeat",
    "promote"
]

# A queue looks like "name": {subOnly: [true|FALSE], isOpen: [TRUE|false] queue: []}
queueList = {}

# A history of the last NEXT call
queueNexted = []
queueNextedMaxSize = 5


# bot.py, below bot object
@bot.event
async def event_ready():
    """Called once when the bot goes online."""
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"And now my watch begins.")
    await resetQueueList()


@bot.event
async def event_error(error, data):
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"And, with my death, my watch comes to an end.")


# bot.py, below event_ready
@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""
    # pprint(ctx.raw_data)

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower() or ctx.author.name.lower() in bots:
        return

    if ctx.author.name.lower() == 'somthebonbon' and "pun" in ctx.content.lower():
        await ctx.channel.send(f"Leave me alone")

    await bot.handle_commands(ctx)

    # bot.py, in event_message, below the bot-ignoring stuff
    print(
        f"{'MOD ' if ctx.author.is_mod else ''}{'SUB ' if ctx.author.is_subscriber else ''}{'TURBO ' if ctx.author.is_turbo else ''}{ctx.author.name}: {ctx.content} at {ctx.timestamp.strftime('%H:%M:%S')}"
    )


@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    content = ctx.content.split()
    separator = " | "
    author = ctx.author

    if len(content) < 2:
        await ctx.send(
            f" @{author.name} Not enough arguments. Please use the correct format: {os.environ['BOT_PREFIX']}queue {separator.join(queueCommands)}"
        )
        return

    subCommand = content[1]

    if subCommand not in queueCommands:
        await ctx.send(
            f"@{author.name} Invalid command. Please use one of the following available commands: {separator.join(queueCommands)}"
        )
        return

    if subCommand in ["join", "j"]:
        await queueJoin(ctx)
    elif subCommand in ["leave", "lv"]:
        await queueLeave(ctx)
    elif subCommand in ["clear", "c"]:
        await queueClear(ctx)
    elif subCommand in ["status", "s"]:
        await queueStatus(ctx)
    elif subCommand in ["list", "ls"]:
        await queueGetList(ctx)
    elif subCommand in ["create"]:
        await queueCreate(ctx)
    elif subCommand in ["remove"]:
        await queueRemove(ctx)
    elif subCommand in ["reset"]:
        await queueReset(ctx)
    elif subCommand in ["open"]:
        await queueOpen(ctx)
    elif subCommand in ["close"]:
        await queueClose(ctx)
    elif subCommand in ["next"]:
        await queueNext(ctx)
    elif subCommand in ["undonext"]:
        await queueUndoNext(ctx)
    elif subCommand in ["repeat"]:
        await queueRepeat(ctx)
    elif subCommand in ["promote"]:
        await queuePromote(ctx)


async def resetQueueList():
    global queueList
    queueList = {
        "tob": {
            "subOnly": False,
            "isOpen": True,
            "queue": ["somthebonbon", "taran", "rizkybizniz", "zionc079"]
        }
    }


async def queueJoin(ctx):
    content = ctx.content.split()
    author = ctx.author
    global queueList
    if 0 <= 2 < len(queueList):
        if content[2] in queueList:
            if queueList[content[2]]['isOpen']:
                # check if queue is sub only and author is a sub
                if (queueList[content[2]]['subOnly'] is True and author.is_subscriber) or not queueList[content[2]][
                    'subOnly']:
                    # check if user already in queue
                    if author.name not in queueList[content[2]]['queue']:
                        queueList[content[2]]['queue'].append(author.name)
                        await ctx.send(f"Adding {author.name} to the {content[2]} queue..")
                    else:
                        await ctx.send(f"@{author.name} You are already in this queue.")
        else:
            await ctx.send(f"@{author.name} the {content[2]} queue does not exist.")
    else:
        # Even though no specific queue is passed
        # If there is only 1 queue
        # we can put the author in that queue
        if len(queueList) == 1:
            # check if user already in queue
            if author.name not in queueList[list(queueList.keys())[0]]['queue'] and \
                    queueList[list(queueList.keys())[0]]['isOpen']:
                queueList[list(queueList.keys())[0]]['queue'].append(author.name)
                await ctx.send(
                    f"Adding {author.name} to the {list(queueList.keys())[0]} queue.."
                )
            else:
                await ctx.send(f"@{author.name} You are already in this queue, or the queue is closed.")
        else:
            await ctx.send(
                f"@{author.name} there are no queues."
            )


async def queueLeave(ctx):
    content = ctx.content.split()
    author = ctx.author
    global queueList
    if len(content) == 3:
        if content[2] in queueList:
            if queueList[content[2]]['isOpen']:
                # check if queue is sub only and author is a sub
                if (queueList[content[2]]['subOnly'] is True and author.is_subscriber) \
                        or not queueList[content[2]]['subOnly']:
                    if author.name in queueList[content[2]]['queue']:
                        queueList[content[2]]['queue'].remove(author.name)
                        await ctx.send(f"Adding {author.name} to the {content[2]} queue..")
                    else:
                        await ctx.send(f"@{author.name} You are not in this queue.")
        else:
            await ctx.send(f"@{author.name} the {content[2]} queue does not exist.")
    elif len(content) == 2:
        # Even though no specific queue is passed
        # If there is only 1 queue
        # we can remove the author from that queue
        if len(queueList) == 1:
            # check if user already in queue
            if author.name not in queueList[list(queueList.keys())[0]]['queue'] and \
                    queueList[list(queueList.keys())[0]]['isOpen']:
                queueList[list(queueList.keys())[0]]['queue'].remove(author.name)
                await ctx.send(
                    f"Adding {author.name} to the {list(queueList.keys())[0]} queue.."
                )
            else:
                await ctx.send(f"@{author.name} You are not in this queue.")
        else:
            await ctx.send(
                f"@{author.name} there are no queues."
            )
    else:
        await ctx.send(f"Use {os.environ['BOT_PREFIX']}q(ueue) leave [<NAME>]")


async def queueStatus(ctx):
    author = ctx.author
    global queueList
    qString = ""
    queueLen = len(queueList)
    index = 0

    for q in queueList:
        if index < queueLen:
            index = index + 1
            qString = qString + f"; {q};{len(queueList[q]['queue'])}{';subOnly' if queueList[q]['subOnly'] else ''};{'open' if queueList[q]['isOpen'] else 'closed'}{', ' if index < len(queueList) else ''}"

    await ctx.send(f"@{author.name} There are currently {len(queueList)} queues{qString}")


async def queueGetList(ctx):
    global queueList
    content = ctx.content.split()

    if len(content) > 3:
        await ctx.send("Too many arguments.")
        return

    if len(content) == 3:
        if content[2] in queueList:
            await ctx.send(f"People in {content[2]} queue: {', '.join(queueList[content[2]]['queue'])}")
        else:
            await ctx.send(f"Queue {content[2]} not found.")
            return
    else:
        if len(queueList) == 1:
            await ctx.send(
                f"People in {list(queueList.keys())[0]} queue: {', '.join(queueList[list(queueList.keys())[0]]['queue'])}")
        else:
            await ctx.send(f"There are multiple queues.")
            return


async def queueClear(ctx):
    global queueList
    author = ctx.author

    if author.is_mod:
        for queue in queueList:
            queue['queue'].clear()
        await ctx.send(f"@{author.name} All queues cleared")
    else:
        await ctx.send(f"@{author.name} You are not in the queue.")


async def queueCreate(ctx):
    global queueList
    author = ctx.author
    content = ctx.content.split()

    """!!q(ueue) create <NAME> <SUBMODE:def=true>"""
    if not author.is_mod:
        return

    if len(content) == 3:
        queueList[content[2]] = {
            "subOnly": False,
            "isOpen": True,
            "queue": []
        }
        await ctx.send(f"Queue {content[2]} created.")
    elif len(content) == 4:
        if content[3].lower() in ['true', 'false']:
            queueList[content[2]] = {
                "subOnly": content[3].lower() == 'true',
                "isOpen": True,
                "queue": []
            }
            await ctx.send(f"Queue {content[2]} created.")
    else:
        await ctx.send(f"use {os.environ['BOT_PREFIX']}q(ueue) create <NAME>")


async def queueRemove(ctx):
    global queueList
    author = ctx.author
    content = ctx.content.split()
    """!!q(ueue) remove <NAME>"""
    if not author.is_mod:
        return

    if len(content) == 3:
        # Check if name exists in queue
        if content[2] in queueList:
            del queueList[content[2]]
            await ctx.send(f"Queue {content[2]} has been removed.")
        else:
            await ctx.send(f"Queue {content[2]} does not exist.")
    else:
        await ctx.send(f"use {os.environ['BOT_PREFIX']}q(ueue) remove <NAME>")


async def queueReset(ctx):
    content = ctx.content.split()
    author = ctx.author
    """!!q(ueue) reset <Y(ES)|N(O)>"""
    if not author.is_mod:
        return

    # Has to have 3rd argument and 3rd arg must be yes or no
    if len(content) != 3 or content[2] not in ['yes', 'no']:
        await ctx.send(f"use {os.environ['BOT_PREFIX']}q(ueue) reset <Y(ES)|N(O)>")

    if author.is_mod and content[2] == 'yes':
        # Reset the queue
        await resetQueueList()
        await ctx.send(f"Resetting queue to default state..")


async def queueOpen(ctx):
    content = ctx.content.split()
    author = ctx.author
    """!!q(ueue) open [<NAME>]"""
    if author.is_mod:
        if len(queueList) >= 1 and len(content) == 3:
            if content[3] in queueList:
                queueList[content[3]]['isOpen'] = True
                await ctx.send(f"Queue \"{content[3]}\" is now open.")
            else:
                await ctx.send(f"Queue \"{content[3]}\" does not exist")
        elif len(queueList) == 1 and len(content) == 2:
            queueList[list(queueList.keys())[0]]['isOpen'] = True
            await ctx.send(f"Queue \"{list(queueList.keys())[0]}\" is now open.")
        else:
            if queueList == 0:
                await ctx.send(f"There are no queues.")
            else:
                await ctx.send(f"There are multiple queues.")
    else:
        return


async def queueClose(ctx):
    content = ctx.content.split()
    author = ctx.author
    """!!q(ueue) close <NAME>"""
    if not author.is_mod:
        return

    if len(queueList) >= 1 and len(content) == 3:
        if content[3] in list(queueList.keys()):
            queueList[content[3]]['isOpen'] = False
            await ctx.send(f"Queue \"{content[3]}\" is now closed.")
        else:
            await ctx.send(f"Queue \"{content[3]}\" does not exist")
    elif len(queueList) == 1 and len(content) == 2:
        queueList[list(queueList.keys())[0]]['isOpen'] = False
        await ctx.send(f"Queue \"{list(queueList.keys())[0]}\" is now closed.")
    else:
        if queueList == 0:
            await ctx.send(f"There are no queues.")
        else:
            await ctx.send(f"There are multiple queues, add a name.")


async def queueNext(ctx):
    global queueList
    global queueNexted
    content = ctx.content.split()
    author = ctx.author
    """!!q(ueue) next [<QUEUE>] <AMOUNT>"""
    if not author.is_mod:
        return

    # A queue name was given
    if len(content) == 4:
        if content[2] in queueList:
            # If the one queue in the list is open
            if queueList[content[2]]['isOpen']:
                sliceSize = int(content[3])
                queueNexted.insert(0, {
                    'queueName': content[2],
                    'nexted': queueList[content[2]]['queue'][:sliceSize]
                })

                await ctx.send(
                    f"Next up in the {content[2]} queue: {', '.join(queueNexted[0]['nexted'])}")
                del queueList[content[2]]['queue'][:sliceSize]
            else:
                await ctx.send(f"No queues are available.")
        else:
            await ctx.send(f"Queue {content[2]} does not exist.")
    # No queue name was passed, check if there is 1 open queue
    elif len(content) == 3:
        # Check if 1 queue is present
        if len(queueList) == 1:
            # If the one queue in the list is open
            if queueList[list(queueList.keys())[0]]['isOpen']:
                sliceSize = int(content[2])
                queueNexted.insert(0, {
                    'queueName': list(queueList.keys())[0],
                    'nexted': queueList[list(queueList.keys())[0]]['queue'][:sliceSize]
                })

                if len(queueNexted) > queueNextedMaxSize:
                    del queueNexted[-1]

                del queueList[list(queueList.keys())[0]]['queue'][:sliceSize]
                await ctx.send(
                    f"Next up in the {list(queueList.keys())[0]} queue: {', '.join(queueNexted[0]['nexted'])}")
            else:
                await ctx.send(f"No queues are available.")
        elif len(queueList) == 0:
            await ctx.send(f"No queues are available.")
        else:
            await ctx.send(f"Queue {content[2]} does not exist.")
    else:
        await ctx.send(f"Use {os.environ['BOT_PREFIX']}q(ueue) next [<QUEUE>] <AMOUNT>")


async def queueUndoNext(ctx):
    global queueList
    global queueNexted
    content = ctx.content.split()
    author = ctx.author

    """Last in first out"""
    """!!q(ueue) undonext"""
    if not author.is_mod:
        return

    if len(content) > 2:
        await ctx.send("Too many arguments.")
        return

    queueToUndo = queueNexted.pop(0)

    if queueToUndo['queueName'] in queueList:
        intersection = [value for value in queueToUndo['nexted'] if
                        value in queueList[queueToUndo['queueName']]['queue']]

        if len(intersection):
            for name in intersection:
                queueToUndo['nexted'].remove(name)

        queueList[queueToUndo['queueName']]['queue'] = queueToUndo['nexted'] + queueList[queueToUndo['queueName']][
            'queue']
        await ctx.send(f"{', '.join(queueToUndo['nexted'])} returned to {queueToUndo['queueName']} queue")
    else:
        await ctx.send(f"Found {queueToUndo['queueName']} in undo list, but the queue does not exist.")


async def queueRepeat(ctx):
    global queueList
    global queueNexted
    content = ctx.content.split()
    author = ctx.author

    """!!q(ueue) repeat"""
    if not author.is_mod:
        return

    if len(content) > 2:
        await ctx.send("Too many arguments.")
        return

    if len(queueNexted):
        await ctx.send(
            f"Last called up: {', '.join(queueNexted[0]['nexted'])} from the {queueNexted[0]['queueName']} queue")
    else:
        await ctx.send("History is empty.")


async def queuePromote(ctx):
    global queueList
    global queueNexted
    content = ctx.content.split()
    queueName = content[2]
    user = content[3]
    position = content[4]
    action = content[5] if len(content) == 6 else 'insert'
    author = ctx.author

    """!!q(ueue) promote <queue> <name> <position> <INSERT|swap>"""

    if not author.is_mod:
        return

    if len(content) < 5:
        """Inserts by default if Swap is not passed as an option"""
        await ctx.send(f"Usage: {os.environ['BOT_PREFIX']}q(ueue) promote <queue> <name> <position> [swap|insert]")
        return

    if len(content) > 6:
        await ctx.send("Too many arguments.")
        return

    if queueName not in queueList:
        await ctx.send("Queue not found.")
        return

    if user not in queueList[queueName]['queue']:
        await ctx.send(f"Name not found in {queueName} queue.")
        return

    if not isInt(position):
        await ctx.send("Invalid position, pass a number.")
        return

    position = int(position)

    if position > (len(queueList[queueName]['queue']) - 1) or position <= 0:
        await ctx.send("Invalid position index.")
        return

    """All validation done, handle command"""
    if len(content) == 5:
        """Insert by default"""
        queueList[queueName]['queue'].remove(user)
        queueList[queueName]['queue'].insert(position - 1, user)
        await ctx.send(f"User {user} moved to position {position} in the {queueName} queue using INSERT mode.")
    else:
        if action == 'insert':
            """Insert"""
            queueList[queueName]['queue'].remove(user)
            queueList[queueName]['queue'].insert(position - 1, user)
            await ctx.send(f"User {user} moved to position {position} in the {queueName} queue using INSERT mode.")
        else:
            """Swap"""
            oldIndex = queueList[queueName]['queue'].index(user)
            newIndex = position - 1
            userToSwapWith = queueList[queueName]['queue'][newIndex]

            """Do the swap"""
            queueList[queueName]['queue'][newIndex], queueList[queueName]['queue'][oldIndex] = \
                queueList[queueName]['queue'][oldIndex], queueList[queueName]['queue'][newIndex]

            await ctx.send(
                f"User {user} moved to position {position} in the {queueName} queue using SWAP mode. {user} was swapped with {userToSwapWith} from position {oldIndex + 1}"
            )


def isInt(value):
  try:
    int(value)
    return True
  except ValueError:
    return False


if __name__ == "__main__":
    bot.run()
