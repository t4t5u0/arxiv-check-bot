# arxiv-check-bot

## What is this
arXivから，登録された単語を検索し，通知する Discord bot

## Usage

### 参加する
以下のリンクをクリックして，僕が立てたBotを追加する


### 自分で建てる場合  


1. [Discord Developer Portal — My Applications](https://discord.com/developers/applications) で，アプリケーションを作る．Bot permission で `Manage Roles` を設定する必要があるので注意する

2. 1 docker-compose を使用する場合
```console
$ git clone https://github.com/t4t5u0/arxiv-check-bot
$ cd arxiv-check-bot
```
docker-compose.yaml にシークレットトークンを書き込む

```console
$ docker-compose up -d
```

2. 2 docker-compose を使用しない場合  
Python<=3.9 が必要です

```console
$ git clone https://github.com/t4t5u0/arxiv-check-bot
$ cd arxiv-check-bot
$ echo -e '[TOKEN]\ntoken=Botのシークレットトークン' > config.ini
$ pip install -r requirements.txt
$ nohup python main.py &
```