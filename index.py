import requests
import json
import inspect
import sys
import discord
import time
from datetime import datetime


from colorama import Fore, Style
from discord.ext import commands
from discord.ext.commands import has_permissions

# Make sure that the user is running Python 3.8 or higher
if sys.version_info < (3, 8):
    exit("Python 3.8 or higher is required to run this bot!")

# Now make sure that the discord.py library is installed or/and is up to date
try:
    from discord import app_commands, Intents, Client, Interaction
except ImportError:
    exit(
        "Either discord.py is not installed or you are running an older and unsupported version of it."
        "Please make sure to check that you have the latest version of discord.py! (try reinstalling the requirements?)"
    )

# ASCII logo, uses Colorama for coloring the logo.
logo = f"""
 _______                        _______               __     
/       \                      /       \             /  |    
$$$$$$$  |  ______   __     __ $$$$$$$  |  ______   _$$ |_   
$$ |  $$ | /      \ /  \   /  |$$ |__$$ | /      \ / $$   |  
$$ |  $$ |/$$$$$$  |$$  \ /$$/ $$    $$< /$$$$$$  |$$$$$$/   
$$ |  $$ |$$    $$ | $$  /$$/  $$$$$$$  |$$ |  $$ |  $$ | __ 
$$ |__$$ |$$$$$$$$/   $$ $$/   $$ |__$$ |$$ \__$$ |  $$ |/  |
$$    $$/ $$       |   $$$/    $$    $$/ $$    $$/   $$  $$/ 
$$$$$$$/   $$$$$$$/     $/     $$$$$$$/   $$$$$$/     $$$$/  
                                                             

"""

# inspect.cleandoc() is used to remove the indentation from the message
# when using triple quotes (makes the code much cleaner)
# Typicly developers woudln't use cleandoc rather they move the text
# all the way to the left
print(logo + inspect.cleandoc(f"""
    Yo :D
    """))

# Try except block is useful for when you'd like to capture errors
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # You can in theory also do "except:" or "except Exception:", but it is not recommended
    # unless you want to suppress all errors
    config = {}


while True:
    # If no token is stored in "config" the value defaults to None
    token = config.get("token", None)
    if token:
        print(f"\n--- Detected token in ./config.json (saved from a previous run). Using stored token. ---\n")
    else:
        # Take input from the user if no token is detected
        token = input("> ")

    # Validates if the token you provided was correct or not
    # There is also another one called aiohttp.ClientSession() which is asynchronous
    # However for such simplicity, it is not worth playing around with async
    # and await keywords outside of the event loop
    try:
        data = requests.get("https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bot {token}"
        }).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"ConnectionError: Discord is commonly blocked on public networks, please make sure discord.com is reachable!")

        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"Timeout: Connection to Discord's API has timed out (possibly being rate limited?)")

        # Tells python to quit, along with printing some info on the error that occured
        exit(f"Unknown error has occurred! Additional info:\n{e}")

    # If the token is correct, it will continue the code
    if data.get("id", None):
        break  # Breaks out of the while loop

    # If the token is incorrect, an error will be printed
    # You will then be asked to enter a token again (while Loop)
    print(f"\nSeems like you entered an invalid token. Please enter a valid token (see Github repo for help).")

    # Resets the config so that it doesn't use the previous token again
    config.clear()


# This is used to save the token for the next time you run the bot
with open("config.json", "w") as f:
    # Check if 'token' key exists in the config.json file
    config["token"] = token

    # This dumps our working setting to the config.json file
    # Indent is used to make the file look nice and clean
    # If you don't want to indent, you can remove the indent=2 from code
    json.dump(config, f, indent=2)


class discordbotdev(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        synced = await self.tree.sync()
        print("Think it's synced")
        print(len(synced))

# Variable to store the bot class and interact with it
# We then do not need any intents to listen to events
client = discordbotdev(intents=Intents())


@client.event
async def on_ready():
    """ This is called when the bot is ready and has a connection with Discord.
        Client ID to make sure you invite the correct bot with correct scopes.
        You can change the bot status in 'game = discord.Game("")'.
    """
    game = discord.Game("test")
    await client.change_presence(status=discord.Status.dnd, activity=game)
    print(inspect.cleandoc(f"""
        Logged in as {client.user} (ID: {client.user.id})
    """), end="\n\n")



############################
###     FUN SECTION      ###
############################

########
## The Rock thing 

@client.tree.command()
async def rock(interaction: Interaction):
    """ Rock """
    # Responds in the console that the command has been ran
    print(f"> {interaction.user} used the command 'rock'.")
    # Create an embed
    embed = discord.Embed(title="", description="")
    embed.set_image(url="https://i.imgflip.com/5ue2x1.jpg")
    # Then responds in the channel with this message
    await interaction.response.send_message(embed=embed)

##########
## HELLO

@client.tree.command()
async def hello(interaction: Interaction):
    """ Says hello or something """
    # Responds in the console that the command has been ran
    print(f"> {interaction.user.mention} used the command 'hello'.")

    # Then responds in the channel with this message
    await interaction.response.send_message(f"Hi **{interaction.user}**")

##########
## PING

@client.tree.command()
async def ping(interaction: Interaction):
    """ Pings the bot """
    # Responds in the console that the command has been ran
    print(f"> {interaction.user} used the command 'ping'.")
    # Create an embed
    embed = discord.Embed(title="", description="", color=0x00ff00)
    embed.add_field(name="🏓 Pong!", value=f"{round(client.latency * 1000)}ms", inline=False)
    # Then responds in the channel with this message
    await interaction.response.send_message(embed=embed)


############################
###     MODS SECTION     ###
############################


########
## userinfo cmd

@client.tree.command()
async def userinfo(Interaction: Interaction, user: discord.User = None):
    """ Shows info about a user """
    # Responds in the console that the command has been ran
    print(f"> {Interaction.user} used the command 'userinfo' on {user}.")
    # If no user is provided, it will default to the user that ran the command
    if user is None:
        user = Interaction.user

    # Then responds in the channel with this message
    # Create an embed
    embed = discord.Embed(title="", description=f"", timestamp=datetime.now())
    embed.set_author(name=str(user))
    embed.set_thumbnail(url=user.avatar)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="Tag", value=user.discriminator, inline=True)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Created at", value=user.created_at.__format__("%A, %d. %B %Y @ %H:%M"), inline=False)
    embed.add_field(name="Joined at", value=user.joined_at.__format__("%A, %d. %B %Y @ %H:%M"), inline=False)
    embed.add_field(name="Is bot ?", value=user.bot, inline=True)
    embed.add_field(name="Mention", value=user.mention, inline=True)
    embed.set_footer(text=f"Requested by {Interaction.user.name}")
    #embed.add_field(name="Avatar", value=f"{user.avatar}", inline=False)

    # Then responds in the channel with this message
    await Interaction.response.send_message(embed=embed)



# Runs the bot with the token you provided
client.run(token)
