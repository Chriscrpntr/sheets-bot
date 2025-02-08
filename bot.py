import re
import syntaxCheck
import discord
import csv

from discord import app_commands
from dotenv import load_dotenv
import os
from urllib.request import urlopen
import xmltodict
from thefuzz import fuzz
from thefuzz import process

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
    "ddropdowns" : "Here is a video on how to create dependant dropdowns by the amazing Dralkyr!\n<https://www.youtube.com/watch?v=fHfVF5AaAjc>\n\nWe also have a sheet!\n[Advanced Dropdown Setups](<https://docs.google.com/spreadsheets/d/1OlRIXjoaUG5Owjd3t9hGfmV7G8EmAKffP7YVPdNGNH0/edit?usp=sharing>)\n"
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

@app_commands.user_install
@tree.command(
    name='search',
    description='Search for an article on Sheets.wiki.')
async def search_command(ctx, *, query: str):
    result = search(query)
    await ctx.response.send_message(result)

@app_commands.user_install
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

@app_commands.user_install
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
    await ctx.response.send_message(syntaxCheck.validate_formula(input_text))

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

client.run(key)
