import sqlite3
from typing import List, Optional, Tuple, Union

# sqlite3.register_adapter(list, lambda l: ';'.join([i for i in l]))
# sqlite3.register_converter(
#     'LIST', lambda s: [item.decode('utf-8') for item in s.split(bytes(b';'))])


def db_create():
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS test_table (
        guild_id      INTEGER PRIMARY KEY,
        channel_id    INTEGER,
        wordlist      JSON);''')
    conn.commit()


def db_connect() -> sqlite3.Connection:
    db_name = 'Info.db'
    conn: sqlite3.Connection = sqlite3.connect(
        db_name,  detect_types=sqlite3.PARSE_DECLTYPES)
    return conn


def db_write(guild_id: int):
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
    for item in c.execute('SELECT * FROM test_table'):
        print(item)
    conn.close()


def db_update(guild_id: int, word: dict):
    # 単語の登録を行う
    # guild_id で検索して，word_listというJSONオブジェクトをいじる
    #
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''SELECT wordlist
        FROM test_table
        WHERE guild_id = ?''', (guild_id,))
    json_obj = (x if (x := c.fetchone()[0]) else '{}')
    print(f'{json_obj=}')
    # json_objの加工
    json_obj: dict = eval(json_obj)
    json_obj.update(word)
    print(json_obj)
    c.execute('''UPDATE test_table 
            SET wordlist = ?
            WHERE guild_id = ?''', (str(json_obj), guild_id))
    conn.commit()
    conn.close()


def db_delete(guild_id: int, del_key: str):
    # 単語の削除を行う
    # guild_id で検索して，word_list からJSONオブジェクトを一部消去
    # Discordのロールの削除は呼び出し元で行う

    conn = db_connect()
    c = conn.cursor()
    c.execute(
        '''SELECT wordlist
        FROM test_table
        WHERE guild_id = ?''', (guild_id,))
    json_obj = c.fetchone()
    try:
        json_obj.pop(del_key)
    except KeyError:
        conn.close()
        return False
    c.execute(
        '''UPDATE test_table
        SET wordlist = ?''', (json_obj,))
    conn.commit()
    conn.close()
    return True


def db_set(guild_id: int, channel_id: int):
    # channel_idを設定する
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT guild_id FROM test_table WHERE guild_id = ?", (guild_id,))
    tmp = c.fetchone()
    print(f'{tmp=}')
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
    for item in c.execute('SELECT * FROM test_table'):
        print(item)
    conn.close()


def db_show(guild_id: Optional[int]) -> Union[Tuple[int, int , dict], List[Tuple[int, int, dict]]]:
    """
    guild_idを設定しなかったら全部返す．
    """
    # 生のレコードを全部返す
    conn = db_connect()
    c = conn.cursor()
    if guild_id is None:
        c.execute('SELECT * FROM test_table')
    else:
        c.execute('SELECT * FROM test_table WHERE guild_id = ?', (guild_id,))
    result: dict = c.fetchone()
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
