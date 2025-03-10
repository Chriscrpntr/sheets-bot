import re
import syntaxCheck
import discord
import csv
from discord.ui import Button, View
from discord import app_commands
from dotenv import load_dotenv
import os
from urllib.request import urlopen
import xmltodict
from thefuzz import fuzz
from thefuzz import process
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load the sitemap from the Sheets Wiki
file = urlopen('https://sheets.wiki/sitemap.xml')
data = file.read()
file.close()

data = xmltodict.parse(data)['urlset']['url']
for i in range(len(data)):
    data[i] = data[i]['loc'].replace('https://sheets.wiki/', '')

def search(query):
    query = query.lower()
    result = process.extractOne(query, data)
    return 'https://sheets.wiki/' + result[0]

load_dotenv()

key = os.getenv('key')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

apis = {
    "map": " Returns an example of map function usage within Google Sheets",
    "scan": "Returns an example of scan function usage within Google Sheets",
    "reduce": "Returns an example of reduce function usage within Google Sheets",
    "lambda": "Returns an example of using lambda within Google Sheets",
    "documentation": "Returns how to use let to incorporate documentation in your formulas for Google Sheets",
}

gaslinks = {
"ExcelGoogleSheets\n<https://www.youtube.com/@ExcelGoogleSheets/search?query=apps%20script>\n",
"Ben Collins\n<https://courses.benlcollins.com/p/apps-script-blastoff>\n",
"Spencer Farris\n<https://www.youtube.com/playlist?list=PLmE9Sui7JoQGqOJvhxYRjOFUtr5kMWUtJ>\n",
}

notablelinks = {
    "[Advanced Dropdown Setups](<https://docs.google.com/spreadsheets/d/1OlRIXjoaUG5Owjd3t9hGfmV7G8EmAKffP7YVPdNGNH0/edit?usp=sharing>)\n",
    "[A History of Crash Bugs](<https://docs.google.com/spreadsheets/d/107B_jSpObwxxYfL_HTBWZtB9cnMQDTraoirpaRUsNLc/edit?gid=582260365#gid=582260365>)\n",
    "[Color Themes](<https://docs.google.com/spreadsheets/d/1Bj5appk-AAGPXuN4gUWfXAQYS772DKmByKqG5owKNzA/edit?usp=sharing>)\n",
    "[Community Practice Problems](<https://docs.google.com/spreadsheets/d/1RZVTUJj_qzugq_WCd7rMjmjzKtUM72Jb5x0RGFAVNnk/edit?gid=890374412#gid=890374412>)\n",
}

commands = {
    "data": "Please [don't ask to ask](https://dontasktoask.com/)!",
    "mockup": "You can use [this tool](https://docs.google.com/forms/d/e/1FAIpQLScf4e8rJpjbDx-SQOH2c2xIaUP-ewnNJoqv9uRAXIrenUvZ_Q/viewform) to create an anonymous mock-up! Please provide sample inputs AND outputs!",
    "xy": "Your problem may be an [XY problem](https://xyproblem.info/), meaning you are asking how to make your solution work, rather than asking about the root problem. This can interfere with assistance—could you please provide information about the root causes?",
    "structure": "[Here's some advice](https://sheets.wiki/books/advice/taming-spreadsheet-data-structure-for-success/) by the excellent Aliafriend about properly formatting your data!",
    "wiki": "You can find our wiki [here](https://sheets.wiki/)!",
    "practice": "Here's a [practice sheet](https://docs.google.com/spreadsheets/d/1RZVTUJj_qzugq_WCd7rMjmjzKtUM72Jb5x0RGFAVNnk/edit?gid=890374412) for intermediate formulae!",
    "timestamp": "[Here is a video](https://www.youtube.com/watch?v=DgqTftdXkTw) by the amazing Dralkyr for timestamping on edit!",
    "apis" : "```We have some Apis for in-sheet examples! Endpoints include:\n" + '\n'.join([f"\n=IMPORTDATA(\"https://aliafriend.com/api/sheets/examples/{api}\")" for api in apis]) + "\n```",
    "learngas" : "Here are some links to start learning Google App Script!\n\n" + '\n'.join([f"\n{link}" for link in gaslinks]),
    "links" : "Spreadsheet Collection\n\n" + '\n'.join([f"{link}" for link in notablelinks]),
    "ddropdowns" : "Here is a video on how to create dependant dropdowns by the amazing Dralkyr!\n<https://www.youtube.com/watch?v=fHfVF5AaAjc>\n\nWe also have a sheet!\n[Advanced Dropdown Setups](<https://docs.google.com/spreadsheets/d/1OlRIXjoaUG5Owjd3t9hGfmV7G8EmAKffP7YVPdNGNH0/edit?usp=sharing>)\n",
    "discord" : "Spreadsheets Discord Link.\n<https://discord.gg/M9GKpPd>",
}

commands['help'] = "I can provide information on Excel and Google Sheets functions! Try `/excel` or `/gsheets` followed by the name of a function. You can also use `/search` followed by a search query to find a relevant article on the Sheets Wiki. Other commands include:\n```" + '\n'.join([f"\n/{command}" for command in commands]) + "\n```"

excel_functions = {}
with open('excel.csv', mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        excel_functions[row['Name'].lower()] = row

gsheets_functions = {}
with open('gsheets.csv', mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        gsheets_functions[row['Name'].lower()] = row

@client.event
async def on_member_join(member):
    welcome_message = f"Welcome to the Spreadsheet Discord Server!, {member.mention}! For long detailed questions post in #questions, for short questions ask in #gsheets or #excel respectively. For more information on the best way to post your question type /help or check out https://sheets.wiki/"
    try:
        await member.send(welcome_message)
    except discord.Forbidden:
        # If the bot cannot send a DM to the user, you might want to handle it:
        print(f"Could not send a welcome message to {member.name}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    excluded_roles = ["Ultimate Newbie", "Spreadmin", "Spreadarator","Trustworthy Spreadsheeter","BOTS"]

    user_roles = [role.name for role in message.author.roles]
    does_not_have_roles = not any(role in excluded_roles for role in user_roles)

    contains_mentions = len(message.mentions) > 0

    is_reply = message.reference is not None

    offender_list = ["aliafriend"]

    is_offender = str(message.author) in offender_list or str(message.author.id) in offender_list

    if does_not_have_roles and contains_mentions and not is_reply and is_offender:
        await message.channel.send(f"{message.author.mention}, Please do not @ mention as specified in the rules.")

    if re.search(r"\bcan\s+someone\s+(help|assist)\b",message.content):
        await message.channel.send(commands['data'])

    if message.channel.name == "gsheets" or message.channel.name == "excel" or message.channel.name == "questions" or message.channel.name == "general" or message.channel.name == "puzzle-general":
        if re.search(r'(https://docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+)', message.content):
            match = re.search(r'https://docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)', message.content)
            sheet_id = match.group(1)  # This captures only the ID after 'd/'

            if not check_edit_permission(sheet_id):  # Pass the sheet ID to the function
                await message.channel.send(f"Please open your spreadsheets to edits or use [Link](https://docs.google.com/forms/d/e/1FAIpQLScf4e8rJpjbDx-SQOH2c2xIaUP-ewnNJoqv9uRAXIrenUvZ_Q/viewform) to create an anonymous sheet for assistance.")

    if message.content.startswith('!'):
        command = message.content.lstrip('!')
        split = command.lower().split(' ')

        if command in commands:
            await message.channel.send(commands[command])

        elif split[0] == 'excel':
            if split[1] in excel_functions:
                func_info = excel_functions[split[1]]
                response = (f"{func_info['Name']}: {func_info['Description']}\n"
                            f"Syntax: `{func_info['Syntax']}`\n"
                            f"More info: {func_info['Link']}")
                await message.channel.send(response)
        elif split[0] == 'gsheets':
            if split[1] in gsheets_functions:
                func_info = gsheets_functions[split[1]]
                response = (f"{func_info['Name']}: {func_info['Description']}\n"
                            f"Syntax: `{func_info['Syntax']}`\n"
                            f"More info: {func_info['Link']}")
                await message.channel.send(response)
        elif split[0] == 'search':
            query = ' '.join(split[1:])
            result = search(query)
            await message.channel.send(result)

        else:
            await message.channel.send("Sorry, I don't recognize that command.")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='search',
    description='Search for an article on Sheets.wiki.')
async def search_command(ctx, *, query: str):
    result = search(query)
    await ctx.response.send_message(result)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='excel',
    description='Search for an Excel function.')
async def search_command(ctx, *, query: str):
    if query in excel_functions:
        func_info = excel_functions[query]
        result = (f"{func_info['Name']}: {func_info['Description']}\n"
                    f"Syntax: `{func_info['Syntax']}`\n"
                    f"More info: {func_info['Link']}")
        await ctx.response.send_message(result)
    else:
        await ctx.response.send_message("That function isn't available!")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='gsheets',
    description='Search for an gsheets function.')
async def search_command(ctx, *, query: str):
    if query in gsheets_functions:
        func_info = gsheets_functions[query]
        result = (f"{func_info['Name']}: {func_info['Description']}\n"
                    f"Syntax: `{func_info['Syntax']}`\n"
                    f"More info: {func_info['Link']}")
        await ctx.response.send_message(result)
    else:
        await ctx.response.send_message("That function isn't available!")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='help',
    description="Information regarding usage of the bot"
)
async def help_command(ctx):
    await ctx.response.send_message(commands['help'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='mockup',
    description= "Create an anonymous mock-up"
)
async def mockup_command(ctx):
    await ctx.response.send_message(commands['mockup'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='data',
    description= "Don't ask to ask"
)
async def data_command(ctx):
    await ctx.response.send_message(commands['data'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='xy',
    description= "Your problem may be an XY problem"
)
async def xy_command(ctx):
    await ctx.response.send_message(commands['xy'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='structure',
    description= "Advice on properly formatting your data"
)
async def structure_command(ctx):
    await ctx.response.send_message(commands['structure'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='wiki',
    description= "The Sheets Wiki"
)
async def wiki_command(ctx):
    await ctx.response.send_message(commands['wiki'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='practice',
    description= "A practice sheet for intermediate formulae!"
)
async def practice_command(ctx):
    await ctx.response.send_message(commands['practice'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='timestamp',
    description= "How to timestamp edits"
)
async def timestamp_command(ctx):
    await ctx.response.send_message(commands['timestamp'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='apis',
    description= "Information on the available Api's"
)
async def apis_command(ctx):
    await ctx.response.send_message(commands['apis'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='localediff',
    description= "Fix locale differences"
)
async def localdiff_command(ctx, *, input_text: str):
    input_text = re.sub(r'\{([^}]*)', lambda match: match.group(0).replace(',', '\\'), input_text)

    # Replace all other ',' with ';'
    updated_text = re.sub(r',', ';', input_text)

    # Send the updated text back
    await ctx.response.send_message(f"Your Locale is different. You'll need to replace your , with ; \n\n```\n{updated_text}\n```")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='learngas',
    description= "Learn Google Apps Script Links"
)
async def learngas_command(ctx):
    await ctx.response.send_message(commands['learngas'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='links',
    description= "Notable Links From Our Collection."
)
async def links_command(ctx):
    await ctx.response.send_message(commands['links'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='ddropdowns',
    description= "How to create dependant dropdowns"
)
async def ddropdowns_command(ctx):
    await ctx.response.send_message(commands['ddropdowns'])

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='syntax',
    description= "Checks for missing commas or parentheses. Warning still in alpha."
)
async def syntaxcheck(ctx, *, input_text: str):
    await ctx.response.send_message("```\n"+ input_text+ "```\n" + syntaxCheck.validate_formula(input_text))



@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name='discord',
    description= "Spreadsheets Discord Link."
)
async def links_command(ctx):
    await ctx.response.send_message(commands['discord'])

PERMANENT_EMBED_MESSAGE_ID = None  # Replace with the ID if you're restarting the bot.

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')
    # Channel ID where the 'permanent' embed will reside
    channel_id = os.getenv('channel')  # Replace with your target channel's ID
    channel_id = int(channel_id)
    global PERMANENT_EMBED_MESSAGE_ID

    # Fetch the target channel
    channel = client.get_channel(channel_id)
    if not channel:
        print("Channel not found or bot lacks permissions.")
        return

    # Check if the embed message already exists
    if PERMANENT_EMBED_MESSAGE_ID:
        try:
            # Retrieve the existing embed message
            message = await channel.fetch_message(PERMANENT_EMBED_MESSAGE_ID)
            print("Permanent embed found. Checking for updates...")

            # Update the embed dynamically to match any changes
            embed = create_embed()  # Get the latest version of the embed

            anonButton = Button(
                label="Create Mockup",
                style=discord.ButtonStyle.link,
                url="https://docs.google.com/forms/d/e/1FAIpQLScf4e8rJpjbDx-SQOH2c2xIaUP-ewnNJoqv9uRAXIrenUvZ_Q/viewform"
            )

            view = View()
            view.add_item(anonButton)

            await message.edit(embed=embed, view=view)
            print("Permanent embed updated successfully.")

        except discord.NotFound:
            # If the message is not found (e.g., deleted), recreate it
            message = await channel.send(embed=create_embed())
            PERMANENT_EMBED_MESSAGE_ID = message.id
            save_message_id(PERMANENT_EMBED_MESSAGE_ID)
        except discord.Forbidden:
            print("Bot doesn't have permission to fetch messages.")
    else:
        # If no message ID exists, send a new embed
        message = await channel.send(embed=create_embed())
        PERMANENT_EMBED_MESSAGE_ID = message.id
        save_message_id(PERMANENT_EMBED_MESSAGE_ID)


def create_embed():
    """Create an embed object."""
    embed = discord.Embed(
        title="Spreadsheets Discord",
        description="Below are some useful tools and links. Remember don't ask to ask!",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Our Sheets Wiki!", value="[Sheets Wiki](https://sheets.wiki)", inline=False)
    embed.add_field(name="Create Mockup", value="[Link](https://docs.google.com/forms/d/e/1FAIpQLScf4e8rJpjbDx-SQOH2c2xIaUP-ewnNJoqv9uRAXIrenUvZ_Q/viewform) to create an anonymous sheet", inline=False)
    embed.add_field(name="Dependant Dropdowns", value="[Advanced Dropdowns](https://docs.google.com/spreadsheets/d/1OlRIXjoaUG5Owjd3t9hGfmV7G8EmAKffP7YVPdNGNH0/edit?gid=623087740#gid=623087740)\n"
                                                      "[Video by Dralkyr!](https://www.youtube.com/watch?v=fHfVF5AaAjc)", inline=False)
    embed.add_field(name="Data Structure", value="[Data Structure](https://sheets.wiki/books/advice/taming-spreadsheet-data-structure-for-success/) is very"
                                                " useful to learn for a better sheets experience.", inline=False)
    embed.add_field(name="Timestamping Edits", value="[How to timestamp edits by Dralkyr!](https://www.youtube.com/watch?v=DgqTftdXkTw)", inline=False)
    embed.add_field(name="Addon", value="Our [Addon](https://script.google.com/d/1H6CQs7kWQtZ49lumL154_SyjSSrMGAYst4EWuOzKh2iaDNh2R8LvBcWk/edit?usp=sharing) that has some useful tools. [Install Guide](https://docs.google.com/spreadsheets/d/1FC7fZi7S_cjAvetYlRVyCKI4X7XFI8WIsbh-ePLGJj4/edit?usp=sharing)", inline=False)
    return embed



def save_message_id(message_id):
    """Save the message ID to a file or database (for persistence). Here, we're using a file."""
    with open("embed_message_id.txt", "w") as file:
        file.write(str(message_id))


def load_message_id():
    """Load the message ID from a file or database."""
    try:
        with open("embed_message_id.txt", "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def check_edit_permission(file_id):
    # Authenticate using a service account
    try:
        creds = Credentials.from_service_account_file("service.json", scopes=[
            "https://www.googleapis.com/auth/drive.metadata",
            "https://www.googleapis.com/auth/drive"
        ])

        # Build the Drive API service
        service = build('drive', 'v3', credentials=creds)

        # Get the permissions
        permissions = service.permissions().list(fileId=file_id).execute()

        # Check for 'anyone' permission with 'writer' role
        for permission in permissions.get("permissions", []):
            if permission.get("type") == "anyone" and permission.get("role") == "writer":
                return True  # Anyone with the link can edit
    except:
        pass
    return False  # No "Anyone with the link can edit" permission


# Load the message ID on startup
PERMANENT_EMBED_MESSAGE_ID = load_message_id()

client.run(key)
