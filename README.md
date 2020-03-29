# 概要
Microsoft Outlook上のデータを取得するためのCLIツールです

# 機能
```
$ otlk --help

Usage: otlk [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  empty   対象ユーザー同士での共通した空き時間を取得
  event   対象ユーザーのイベントを取得
  me      自身のユーザー情報を表示
  people  ユーザー一覧をを表示
```

- 細かなオプションは、それぞれのコマンドの`--help`で確認のこと

## 自分のアカウントを確認

```
$ otlk me

|                | me                                   |
|:---------------|:-------------------------------------|
| id             | xxxx                                 |
| displayName    | hase hiro                            |
| user_id        | me                                   |
| mobilePhone    |                                      |
| officeLocation |                                      |
| mobilePhone    |                                      |
```

## 所属するグループのユーザーを確認
```
$ otlk people

|     | displayName                                                       | user_id                            | companyName      |
|----:|:------------------------------------------------------------------|:-----------------------------------|:-----------------|
|   0 | xxxx                                                              | xxx@exapmle.com                    |                  |
|   1 | yyyy                                                              | yyy@example.com                    | ABC              |
|   2 | zzzz                                                              |                                    |                  |
```

## 予定一覧を確認
```
$ otlk [ユーザー名]  --start [YYYY/mm/dd HH/MM] --end [YYYY/mm/dd HH/MM] 

|    | subject                                                                                  | locations            | start.dateTime      | end.dateTime        |
|---:|:-----------------------------------------------------------------------------------------|:---------------------|:--------------------|:--------------------|
|  0 | subjectA                                                                                 | []                   | 2020-03-02 18:00:00 | 2020-03-02 18:30:00 |
|  1 | subjectB                                                                                 | []                   | 2020-03-02 19:00:00 | 2020-03-02 20:00:00 |
...
```
- `-d`オブションをつけることで、参加者一覧や、終日の予定かどうかなどの、付属情報も確認可能
- ユーザー名を省略した場合、自身の予定が出力される
- `--start[end]`の時間以下は省略可能。また、それぞれのオプションを省略した場合、直近の予定が出力される

## 指定したユーザー同士の空いている時間を確認
```
$ otlk empty [ユーザー名1] [ユーザー名2]  ... --minutes [確保したい時間(分) --start [YYYY/mm/dd HH/MM] --end [YYYY/mm/dd HH/MM] 

|    | from             | to               |
|---:|:-----------------|:-----------------|
|  0 | 2020/03/29 18:45 | 2020/03/30 10:00 |
|  1 | 2020/03/30 13:00 | 2020/03/30 13:30 |
|  2 | 2020/03/30 13:45 | 2020/03/30 16:00 |
|  3 | 2020/03/30 17:30 | 2020/03/30 18:00 |
```

- `--start[end]`の時間以下は省略可能。また、それぞれのオプションを省略した場合、直近数日の予定が出力される


# 設定方法
## インストール
```
pip install -U otlk
```

## 認証
- [公式のアプリケーションの認証方法](https://docs.microsoft.com/ja-jp/outlook/rest/get-started)に従い、アプリケーションを登録し、`client_id`, `client_secret`および、`refresh_token`を取得
- 発行時のスコープには以下を含める
```
[
    "openid",
    "offline_access",
    "User.Read",
    "Calendars.Read",
    "Calendars.Read.Shared",
    "People.Read"
]
```

## credential.jsonを作成
上記の情報から、json形式のファイルを作成する
```
{
"client_id": "xxxx",
"client_secret": "yyyy",
"refresh_token": "zzzz"

}
```

## 環境変数の設定
上記の`credential.json`のPATHを、以下の環境変数に設定
```
 export OTLK_CREDENTIAL="[path]/[to]/credential.json"
```

## 確認
下記のコマンドで、自身の情報が返ってくれば成功
```
otlk me
```
