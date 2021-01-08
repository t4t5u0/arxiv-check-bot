import configparser

import discord
from discord.ext import commands
from discord.ext.commands import Bot


class UserHelp(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = 'コマンド: '
        self.no_category = 'other'
        self.command_attrs['help'] = 'コマンド一覧と簡単な説明を表示'

    def command_not_found(self, string):
        return f'{string} というコマンドは見つかりませんでした'

    def get_ending_note(self):
        return (
            f'このBotは`arxiv.org`に新規投稿された論文をチェックするものです\n\n'
            f'各コマンドの説明: {prefix}help <コマンド名>\n')



config = configparser.ConfigParser()
config.read('./config.ini')
TOKEN = config['TOKEN']['token']

prefix = '/'
bot = Bot(command_prefix=prefix, help_command=UserHelp())
bot.load_extension('cog.arxiv_check')


if __name__ == "__main__":
    bot.run(TOKEN)
