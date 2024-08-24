import discord
import csv
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv('key')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

commands = {
    "mockup": "You can use [this tool](https://docs.google.com/forms/d/e/1FAIpQLScf4e8rJpjbDx-SQOH2c2xIaUP-ewnNJoqv9uRAXIrenUvZ_Q/viewform) to create an anonymous mock-up! Please provide sample inputs AND outputs!",
    "data": "Please [don't ask to ask](https://dontasktoask.com/)!",
    "xy": "Your problem may be an [XY problem](https://xyproblem.info/), meaning you are asking how to make your solution work, rather than asking about the root problem. This can interfere with assistance—could you please provide information about the root causes?",
    "structure": "[Here's some advice](https://sheets.wiki/books/advice/taming-spreadsheet-data-structure-for-success/) by the excellent Aliafriend about properly formatting your data!",
    "wiki": "You can find our wiki [here](https://sheets.wiki/)!"
}

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
async def on_message(message):
    if message.author == client.user:
        return
    
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
        else:
            await message.channel.send("Sorry, I don't recognize that command.")

client.run(key)