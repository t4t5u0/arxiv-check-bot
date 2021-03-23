from collections import UserList
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import arxiv
import discord
import pytz
from discord.ext import commands, tasks
from googletrans import Translator

try:
    from app.libs.database import *
except ModuleNotFoundError:
    from libs.database import *


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
    """
    論文クラス\n

    link: str \n
    title: str \n
    abst: str \n
    j_abst: str \n
    keywords: dict # {"role1": roleid1, "role2": roleid2, ...} \n
    """
    link: str
    title: str
    abst: str
    j_abst: str
    keywords: dict  # {"role1": roleid1, "role2": roleid2, ...}

    def __add__(self, other):
        if self.link == other.link:
            self.keywords += other.keywords

    # await ctx.send のときに使う
    def show(self, _guild: discord.Guild) -> str:
        """
        表示用の文字列を返す．\n
        _guild: 表示対象のguild
        """
        role_ids = self.keywords.values()
        # print(f'{self.keywords=}')
        # print(f'{role_ids=}')
        # print(f'{_guild=}')
        roles = list(filter(lambda x: x is not None,
                            [_guild.get_role(role_id) for role_id in role_ids]))
        # print(roles)
        if not roles:
            roles_mentions = [""]
        else:
            roles_mentions: list[str] = [role.mention for role in roles]
        mentions_string = ' '.join(roles_mentions)
        return (
            f'**{self.title}**\n'
            f'{mentions_string}\n'
            f'{self.link}\n'
            f'{self.j_abst}\n'
            f'{"-"*20}'
        )


class Papers(UserList):
    """
    論文のリスト\n
    self.data: list # これが本体
    """

    def __init__(self, arg: list[Paper]):
        arg = arg if arg else []
        super().__init__(arg)
        self.data: list[Paper]

    def __add__(self, other: list[Paper]):
        """
        \+演算子．appendを回している
        """
        for paper in other:
            self.append(paper)

    def append(self, other: Paper):
        """
        Paperのlinkが重複していたらkeywordをまとめる．そうでなければ末尾に追加する
        """
        links = [paper.link for paper in self.data]
        if (i := self.link_index(links, other.link)) != -1:
            self.data[i].keywords.update(other.keywords)
        else:
            self.data.append(other)

    def link_index(self, l: list[str], x: str) -> int:
        """
        linkが重複しているかの判定\n
        重複していたら0オリジンのインデックスを返す\n
        重複していなかったら-1を返す
        """
        if x in l:
            return l.index(x)
        else:
            return -1


class ArxivCheckCog(commands.Cog, name="checker"):
    """
    Botのメイン部分．
    検索する単語を追加・削除する処理と，
    論文通知を定期実行する処理に分かれる
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.word_list: list[dict] = []
        self.guild_id_list = []
        self.data = []

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Bot起動時に呼ばれる．
        定期実行関数の起動を行う
        """
        db_create()
        print('login')
        self.send_periodically.start()
        await self.bot.change_presence(activity=discord.Game(name='/help'))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        db_write(guild.id)

    @commands.command()
    async def neko(self, ctx: commands.Context):
        """にゃうと返す"""
        _author: Union[discord.User, discord.Member] = ctx.author
        await ctx.send(f'{_author.mention} にゃう')

    @commands.command(name="set")
    async def _set(self, ctx: commands.Context):
        """
        論文を送信するチャンネルを設定する
        """
        # channel_id を設定
        # db_set
        # print(ctx.guild.id, ctx.channel.id)
        _guild: Optional[discord.Guild] = ctx.guild
        _channel: Optional[discord.TextChannel] = ctx.channel
        db_set(_guild.id, _channel.id)
        await ctx.send(f'{_channel.mention}を送信対象に設定します')

    @commands.command(name='add')
    async def _add(self, ctx: commands.Context, *args):
        """
        検索したい単語を追加
        追加したい単語と同名のロールを作成し，メンションによって通知が送信されるようにします
        """
        _guild: Optional[discord.Guild] = ctx.guild
        # await ctx.send(f'{_guild.name}, {_guild.id}')

        # async def role(self, x, guild):
        #     result = discord.utils.get(_guild.roles, name=x)
        #     if result is None:
        #         # create role
        #         await _guild.create_role(name=x)

        arg_dict = []
        for arg in args:
            # ここでロールの存在チェックをしないと無限にロールが生成される
            role: Optional[discord.Role] = discord.utils.get(
                _guild.roles, name=arg)
            # ロールが存在しなかったら
            if role is None:
                role: discord.Role = await _guild.create_role(name=arg, mentionable=True)
            # Noneチェックをしたので，Optional を外せる
            role: discord.Role
            # メンションできない場合
            if not role.mentionable:
                pass
            # await ctx.send(role.name)
            # x = {"role_name": role.name, "role_id": role.id}
            x = {role.name: role.id}
            arg_dict.append(role.name)
            db_update(_guild.id, x)

        # arg_dict = [{"key":x, "role": r} for x in args if (r := self.role(x, _guild)) is not None]
        # self.word_list.append(arg_dict)
        # await ctx.send(arg_dict)
        await ctx.send(
            "検索ワードを追加しました\n" +
            '[' + ', '.join(role_name for role_name in arg_dict) + ']'
        )

    @commands.command(name="delete")
    async def _delete(self, ctx: commands.Context, *args):
        """
        検索対象の単語とロールを削除する
        単語が一致しなかったら何もしない
        ロールが見つからなかった何もしない
        """

        for role_name in args:
            role: Optional[discord.Role] = db_delete(ctx.guild, role_name)
            if role:
                await ctx.send(f'{role_name} を削除しました')
                await role.delete()
                continue
            await ctx.send(f'{role_name} というワードは存在しません')

    @commands.command()
    async def show(self, ctx: commands.Context):
        """検索対象の単語一覧を表示"""
        # TODO:
        _, _, word_list = db_show(ctx.guild.id)[0]
        # print(f'{word_list=}')
        word_list: dict = eval(word_list)
        if not word_list:
            await ctx.send('単語が登録されていません')
            return
        for i, item in enumerate(word_list.keys(), start=1):
            await ctx.send(f'{i:2}. {item}')

    @commands.command(name='roles')
    async def _roles(self, ctx: commands.Context):
        """
        ロール一覧を表示
        """

        _guild: Optional[discord.Guild] = ctx.guild
        if _guild:
            roles: list[discord.Role] = _guild.roles
            for role in roles:
                await ctx.send(role)

    # 定期実行する関数

    @tasks.loop(minutes=1)
    async def send_periodically(self):
        """
        論文を毎日18:00に送信する
        feature: サーバごとに送信する時間を変更する
        """
        # https://discordpy.readthedocs.io/ja/latest/ext/tasks/index.html
        now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%H:%M")
        if now == '18:00':
            # if True:

            # print(f'{db_show()=}')
            for result in db_show(None):
                # ここNone渡す必要あるか？
                # print(f'{result=}')
                guild_id, channel_id, keywords = result
                guild_id, channel_id, keywords = int(
                    guild_id), int(channel_id), eval(keywords)
                keywords: dict
                channel = self.bot.get_channel(channel_id)
                papers: Papers = self.get_papers(
                    guild_id, channel_id, keywords)
                # print(len(result))
                # print(result)
                # print(now)

                channel: discord.TextChannel = self.bot.get_channel(channel_id)
                # await channel.send(now + '時だよ')
                guild: discord.Guild = self.bot.get_guild(guild_id)
                # print(f'{ctx}')
                paper: Paper
                for paper in papers:
                    await channel.send(paper.show(guild))

    @commands.command()
    async def issue(self, ctx: commands.Context):
        await ctx.send('https://github.com/t4t5u0/arxiv-check-bot/issues')

    # https://qiita.com/_yushuu/items/83c51e29771530646659
    def trans(self, text: str) -> str:
        "アブスト翻訳用のヘルパー関数"
        tr = Translator()
        result = ""
        while True:
            try:
                result: str = tr.translate(text, src="en", dest="ja").text
                break
            except Exception as e:
                pass
        return result

    def get_papers(self, guild_id: int, channel_id: int, keywords: dict) -> Papers:
        """
        arXivから論文から取得する関数．あとで最適化する
        """
        dt_now = datetime.now(pytz.timezone('Asia/Tokyo'))
        dt_old = dt_now - timedelta(days=1)  # 1日前
        dt_day = dt_old.strftime('%Y%m%d')
        dt_last = dt_day + '235959'
        # print(dt_now, dt_old)
        # print(dt_day, dt_last)
        # words = list(keywords.keys())
        # role_id = keywords.values()
        result = Papers(None)
        for word, value in keywords.items():
            q = f'all:"{word}" AND submittedDate:[{dt_day} TO {dt_last}]'
            papers = arxiv.query(
                query=q, sort_by='submittedDate', sort_order='ascending'
            )

            # print(q)

            # result = []
            for paper in papers:
                abst = ''.join(paper["summary"].splitlines())
                # print(abst[:30])
                p = Paper(
                    link=paper["pdf_url"],
                    title=paper["title"].replace('\n', ' '),
                    abst=abst,
                    j_abst=self.trans(abst),
                    # 1つ分を挿入する．全部挿入してたので全ロールをメンションしてた
                    keywords={word: value}
                )
                result.append(p)
        return result

    @commands.command()
    async def test_get_paper(self, ctx: commands.Context, arg):
        print("test run")
        await ctx.send("`test run`")
        for paper in self.get_papers(arg):
            await ctx.send(f'`{paper.title}`')
        await ctx.send("`test done`")

    @commands.command()
    async def test_get_one_paper(self, ctx: commands.Context, arg: str):
        _guild: Optional[discord.Guild] = ctx.guild
        _channel: Optional[discord.TextChannel] = ctx.channel
        await ctx.send("`test run`")
        _, _, word_list = db_show(_guild.id)[0]
        word_list: dict = eval(word_list)
        papers = self.get_papers(_guild.id, _channel.id, {
                                 arg: word_list[arg]})  # !!!!!!
        if not papers:
            await ctx.send("no result")
            await ctx.send("`test done`")
            return
        paper: Paper = papers[0]
        await ctx.send(paper.show(ctx.guild))
        await ctx.send("`test done`")


def setup(bot: commands.Bot):
    return bot.add_cog(ArxivCheckCog(bot))
