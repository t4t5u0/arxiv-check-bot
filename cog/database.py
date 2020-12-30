import sqlite3

# sqlite3.register_adapter(list, lambda l: ';'.join([i for i in l]))
# sqlite3.register_converter(
#     'LIST', lambda s: [item.decode('utf-8') for item in s.split(bytes(b';'))])


def db_create():
    db_name = "Info.db"
    conn = sqlite3.connect(db_name,  detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS test_table (
        guild_id      INTEGER,
        channel_id    INTEGER,
        wordlist      JSON
    );
    ''')
    conn.commit()


def db_write():
    # writeというよりupsirt ?
    # guild_id を登録 これが主キー
    # set コマンド的なやつで
    # guild_id が存在しなかったら追加
    # channel_id は 上書き
    pass

def db_update():
    # 単語の登録を行う
    # guild_id で検索して，word_listというJSONオブジェクトをいじる
    # 
    pass


def db_delete():
    # 単語の削除を行う
    # guild_id で検索して，word_list からJSONオブジェクトを一部消去
    # Discordのロールの削除は呼び出し元で行う
    pass


"""
{
    "guild_id": int,
    "channel_id": int,
    "wordlist": [
        {"word": str, "role_id" :int},
    ]
}
"""
