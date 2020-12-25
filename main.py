import configparser

import discord
from discord.ext.commands import Bot

config = configparser.ConfigParser()
config.read('./config.ini')
TOKEN = config['TOKEN']['token']

bot = Bot(command_prefix='/')
bot.load_extension('cog.arxiv_check')

if __name__ == "__main__":
    bot.run(TOKEN)