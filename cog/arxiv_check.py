import configparser
from datetime import datetime
import time
from dataclasses import dataclass
from typing import List, Tuple

import arxiv
import discord
import pytz
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from googletrans import Translator

# 検索するべき単語の追加削除
# 単語リストが更新されたとき，それに付随するロールを作成する
# ある論文に単語リスト中のキーワードが含まれていたら，まとめて，メンションする
# 検索したい単語について，ロールを追加．自動的にメンションする
# アブストラクトを日本語訳

# 検索は１日１回．18:00 JSTにおこなう

# 実装するコマンド
#  - add
#  - delete
#  - show
#  - now
#  - help


# @bot.command()
# async def

@dataclass
class Paper:
    link: str
    title: str
    abst: str
    j_abst: str
    keywords: Tuple[str]

class ArxivCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_list: List[dict] = []
        # self.periodically.start()
        # self.bot = Bot(command_prefix='!')
        # self.bot.load_extension('cog.sort_riddle')

    @commands.Cog.listener()
    async def on_ready(self):
        print('login')
        self.periodically.start()
        await self.bot.change_presence(activity=discord.Game(name='/help'))


    @commands.command()
    async def neko(self, ctx):
        await ctx.send('にゃう')

    @commands.command()
    async def add(self, ctx, *args):
        _guild = ctx.guild

        def role(x):
            result = discord.utils.get(_guild.roles, name=x)
            if result is None:
                # create role
                _guild.create_role(name=x)
            return result 


        arg_dict = {x: role(x) for x in args if role(x) is not None}
        self.word_list.append(arg_dict)
        await ctx.send("検索ワードを追加しました[" 
                + ' '.join(arg for arg in arg_dict.keys) + ']')

    @commands.command()
    async def delete(self, ctx, *args):
        # TODO:
        pass

    # 定期実行する関数
    @tasks.loop(minutes=1)
    async def periodically(self):
        # https://discordpy.readthedocs.io/ja/latest/ext/tasks/index.html
        now = datetime.now().strftime("%H:%M")
        if now == '18:00':
        # print(now)
            channel  = self.bot.get_channel(761580345090113569)
            await channel.send(now + '時間だよ')




def setup(bot):
    return bot.add_cog(ArxivCheckCog(bot))

