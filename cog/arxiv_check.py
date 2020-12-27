import csv
import json
import configparser
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

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
#  - [ ] add
#  - [ ] delete
#  - [ ] show
#  - [ ] now
#  - [x] help

# @bot.command()
# async def


@dataclass
class Paper:
    link: str
    title: str
    abst: str
    j_abst: str
    keywords: Set[str]

    def __add__(self, other):
        if self.link == other.link:
            self.keywords += other.keywords

    # await ctx.send のときに使う
    def __str__(self) -> str:
        return (
            f'{self.title}\n'
            f'{self.link}\n'
            f'{self.j_abst}\n'
        )
        # ロールのメンション処理を追加する
        # role.mention


class ArxivCheckCog(commands.Cog, name="checker"):
    # guild id と　channel id  を保持しないといけない
    # ワードごとに設定できるのが理想
    def __init__(self, bot):
        self.bot = bot
        self.word_list: List[dict] = []
        self.guild_id_list = []
        self.data = []

        # with open('./data/guild_id_list.csv') as f:
        #     self.guild_id_list = [int(y) for x in csv.reader(f) for y in x]

        # with open('./data/guild_info.json') as f:
        #     self.data = json.load(f)
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
        """にゃうと返す"""
        await ctx.send(f'{ctx.author.mention} にゃう')

    @commands.command()
    async def add(self, ctx, *args):
        """
        検索したい単語を追加
        追加したい単語と同名のロールを作成し，メンションによって通知が送信されるようにします
        """
        _guild = ctx.guild
        await ctx.send(f'{_guild.name}, {_guild.id}')

        # async def role(self, x, guild):
        # result = discord.utils.get(_guild.roles, name=x)
        # if result is None:
        #     # create role
        #     await _guild.create_role(name=x)

        arg_dict = []
        for arg in args:
            role = await _guild.create_role(name=arg, mentionable=True)
            await ctx.send(role.name)
            arg_dict.append(
                {"role_name": role.name, "role_id": role.id}
            )

        # arg_dict = [{"key":x, "role": r} for x in args if (r := self.role(x, _guild)) is not None]
        self.word_list.append(arg_dict)
        await ctx.send(arg_dict)
        await ctx.send("検索ワードを追加しました["
                       + ' ,'.join(arg["role_name"] for arg in arg_dict) + ']')

    @commands.command()
    async def delete(self, ctx, *args):
        """
        検索対象の単語を消す
        一致しなかったらそのまま
        """
        # TODO:
        pass

    @commands.command()
    async def show(self, ctx):
        """検索対象の単語一覧を表示"""
        # TODO:
        for item in self.word_list[0]:
            await ctx.send(item["key"])

    # 定期実行する関数

    @tasks.loop(minutes=1)
    async def periodically(self):
        # https://discordpy.readthedocs.io/ja/latest/ext/tasks/index.html
        now = datetime.now().strftime("%H:%M")
        if now == '18:00':
            # print(now)
            channel = self.bot.get_channel(761580345090113569)
            await channel.send(now + '時間だよ')

    # https://qiita.com/_yushuu/items/83c51e29771530646659
    def trans(self, text) -> str:
        tr = Translator()
        result = ""
        while True:
            try:
                result = tr.translate(text, src="en", dest="ja").text
                break
            except Exception as e:
                #tr = Translator()
                # tr = Translator(service_urls=['translate.googleapis.com'])
                pass
        return result

    def get_paper(self, keyword) -> List[Paper]:
        dt_now = datetime.now(pytz.timezone('Asia/Tokyo'))
        dt_old = dt_now - timedelta(days=30)
        dt_day = dt_old.strftime('%Y%m%d')
        dt_last = dt_day + '235959'
        # print(dt_now, dt_old, dt_day, dt_last)

        q = f'all:"{keyword}" AND submittedDate:[{dt_day} TO {dt_last}]'
        papers = arxiv.query(
            query=q, sort_by='submittedDate', sort_order='ascending'
        )
        print(q)

        result = []
        for paper in papers:
            abst = ' '.join(paper["summary"].splitlines())
            # print(abst[:30])
            p = Paper(
                link=paper["pdf_url"],
                title=paper["title"],
                abst=abst,
                j_abst=self.trans(abst),
                keywords={keyword}
            )
            result.append(p)
        return result

    @commands.command()
    async def test_get_paper(self, ctx):
        print("test run")
        await ctx.send("`test run`")
        for paper in self.get_paper("deep"):
            await ctx.send(f'`{paper.title}`')
        await ctx.send("`test done`")

    @commands.command()
    async def test_get_one_paper(self, ctx):
        await ctx.send("`test run`")
        paper = self.get_paper("deep")[0]
        await ctx.send(paper)
        await ctx.send("`test done`")


def setup(bot):
    return bot.add_cog(ArxivCheckCog(bot))
