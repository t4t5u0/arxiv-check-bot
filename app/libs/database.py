import sqlite3
from typing import List, Literal, Optional, Tuple, Union
from pathlib import Path

import discord


def db_connect() -> sqlite3.Connection:
    "データベースに接続するヘルパー関数．閉じ忘れないよう"
    path = Path.cwd().glob('**/Info.db')
    db_name = str(list(path)[0])
    conn: sqlite3.Connection = sqlite3.connect(
        db_name,  detect_types=sqlite3.PARSE_DECLTYPES)
    return conn


def db_create():
    '''CREATE TABLE IF NOT EXISTS test_table (\n
        guild_id      INTEGER PRIMARY KEY, \n
        channel_id    INTEGER, \n
        wordlist      JSON);'''

    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS test_table (
        guild_id      INTEGER PRIMARY KEY,
        channel_id    INTEGER,
        wordlist      JSON);''')
    conn.commit()


def db_write(guild_id: int):
    "guild_idを書き込む(主キー)．やってることはUPSERT"
    # writeというよりupsirt ?
    # guild_id を登録 これが主キー
    # set コマンド的なやつで
    # guild_id が存在しなかったら追加
    # channel_id は 上書き
    conn = db_connect()
    c = conn.cursor()
    json_obj = c.execute(
        '''SELECT wordlist
        FROM test_table
        WHERE guild_id = ?''', (guild_id,))
    if json_obj is None:
        c.execute(
            """INSERT INTO test_table(guild_id) VALUES(?)""", (guild_id,))
    conn.commit()
    # for item in c.execute('SELECT * FROM test_table'):
    #     print(item)
    conn.close()


def db_update(guild_id: int, word: dict):
    """
    単語の登録を行う\n
    guild_id で検索して，word_listというJSONオブジェクトをいじる
    """
    # 単語の登録を行う
    # guild_id で検索して，word_listというJSONオブジェクトをいじる
    #
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''SELECT wordlist
        FROM test_table
        WHERE guild_id = ?''', (guild_id,))
    x = c.fetchone()[0]
    json_obj = None
    if x is None:
        json_obj = "{}"
    else:
        json_obj = (x if x else '{}')
    # json_objの加工
    json_obj: dict = eval(json_obj)
    json_obj.update(word)
    c.execute('''UPDATE test_table 
            SET wordlist = ?
            WHERE guild_id = ?''', (str(json_obj), guild_id))
    conn.commit()
    conn.close()


def db_delete(guild: discord.Guild, del_key: str) -> Union[tuple[Literal[False], None], tuple[Literal[True], Optional[discord.Role]]]:
    """
    単語の削除を行う\n
    guild_id で検索して，word_list からJSONオブジェクトを一部消去\n
    Discordのロールの削除は呼び出し元で行う"""

    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''SELECT wordlist
        FROM test_table
        WHERE guild_id = ?''', (guild.id,))
    json_obj = c.fetchone()
    # 辞書型に戻す
    json_obj: dict = eval(json_obj[0])
    role_id: int
    try:
        role_id = json_obj.pop(del_key)
    except KeyError:
        conn.close()
        return False, None
    c.execute(
        '''UPDATE test_table
        SET wordlist = ?''', (str(json_obj),))
    conn.commit()
    conn.close()
    role: Optional[discord.Role] = discord.utils.get(
        guild.roles, id=role_id)
    return True, role


def db_set(guild_id: int, channel_id: int):
    "channel_idを設定する"
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT guild_id FROM test_table WHERE guild_id = ?", (guild_id,))
    tmp = c.fetchone()
    # print(f'{tmp=}')
    if tmp is None:
        c.execute(
            '''INSERT INTO test_table(guild_id, channel_id)
            VALUES(?, ?)''', (guild_id, channel_id))
    else:
        c.execute(
            '''UPDATE test_table
            SET channel_id = ?
            WHERE guild_id = ?''',
            (channel_id, guild_id))
    conn.commit()
    # for item in c.execute('SELECT * FROM test_table'):
    # print(f'{item=}')
    conn.close()


def db_show(guild_id=None) -> List[dict]:
    """
    guild_idをもとに\n
    `guild_id: int, channel_id: int , json_obj: str(dict)` を返す\n
    guild_idを設定しなかったら全部返す．
    """
    # 生のレコードを全部返す
    conn = db_connect()
    c = conn.cursor()
    if guild_id is None:
        c.execute('SELECT * FROM test_table')
    else:
        c.execute('SELECT * FROM test_table WHERE guild_id = ?', (guild_id,))
    result: list[dict] = c.fetchall()
    conn.close()
    return result


'''
{
    'guild_id': int,
    'channel_id': int,
    'wordlist': json
        {'role1': role1_id, 'role2': role2_id},
}
'''
