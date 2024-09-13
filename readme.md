Makeshop注文情報取得
---------------------
## 環境
- python : 3.11.1
- certifi : 2024.7.4
- charset-normalizer : 3.3.2
- idna : 3.7
- requests : 2.32.3
- urllib3 : 2.2.2

## 設定
`MakeShop.ini.sample`を参考に`MakeShop.ini`を作成

```
[MakeShop]
END_POINT=https://www.example.com/
TOKEN=PAT.0000000000000000000000000000000000000000000000000000000000000000
API_KEY=0000000000000000000000000000000000000000000000000000000000000000
SECRET_KEY=0000000000000000000000000000000000000000000000000000000000000000
```
- [MakeShop]  
    MakeShopにapps developer登録後、アプリ開発申請すると発行される情報。
    - END_POINT  
        APIの接続先URL。  
    - TOKEN  
        APIで使用する永続トークン。  
    - API_KEY  
        APIで使用するキー。  
    - SECRET_KEY  
        APIで使用するシークレットキー。  

```
[SearchOrder]
DELIVERY_STATUS=Y
SORT_ORDER=ASC
PAGE=1
LIMIT=1000
PRODUCT_NAME=.*テスト.*
GROUP_NAME=^(?!.*テスト).*$
START_DATE=2024-01-01 00:00:00
END_DATE=2024-12-31 23:59:59
```
- [SearchOrder]  
    注文情報を取得する際の条件を指定する。
    - DELIVERY_STATUS  
      配送状況の指定。
      [SearchOrderRequest](https://developers.makeshop.jp/api/graphql/index.html#definition-SearchOrderRequest)
        - `N` : 未処理
        - `Y` : 配送
        - `C` : キャンセル
        - `R` : 返送  
    - SORT_ORDER  
      ソート順の指定。[SortOrder](https://developers.makeshop.jp/api/graphql/index.html#definition-SortOrder)
        - `ASC` : 昇順
        - `DESC` : 降順
    - PAGE  
      取得を開始するページ番号の指定。基本は`1`でOK。
    - LIMIT  
      1ページで取得可能な件数の指定。基本は`1000`でOK。
    - PRODUCT_NAME  
      取得したい商品名を正規表現で指定。  
      例）
        - 「テスト」を含む商品の場合 : `.*テスト.*`
        - 「テスト」を**含まない**商品の場合 : `^(?!.*テスト).*$`
    - GROUP_NAME  
      取得したいグループのグループ名を正規表現で指定。  
      例）
        - 「テスト」を含むグループの場合 : `.*テープ.*`
        - 「テスト」を**含まない**グループの場合 : `^(?!.*テスト).*$`

    - START_DATE  
      取得したい注文の開始日時を`yyyy-mm-dd HH:MM:SS`で指定。  
      例）
        - 2024年1月1日 午前0時0分 以降 : `2024-01-01 00:00:00`
    - END_DATE  
      取得したい注文の終了日時を`yyyy-mm-dd HH:MM:SS`で指定。  
      例）
        - 2024年12月31日 午後11時59分 以前 : `2024-12-31 23:59:59`
      

## 実行結果
```
$ python main.py
-----------------------------
注文番号 : P180941172630907436
会員ID   : X241151
都道府県 : 東京都
日付     : 2024-09-06 11:24:51
注文年月 : 202409
グループ :
処理状況 : 配送
  商品名1
    商品名     : テスト商品
    商品価格   : 10,000
    個数       : 1
    商品コード : 000000000001
注文合計金額 : 10,000
-----------------------------
注文番号 : P180941415222651772
会員ID   : 240906000001
都道府県 : 北海道
日付     : 2024-09-06 12:03:24
注文年月 : 202409
グループ : テスト
処理状況 : 配送
  商品名1
    商品名     : テスト商品
    商品価格   : 10,000
    個数       : 1
    商品コード : 000000000001
  商品名2
    商品名     : テスト商品2
    商品価格   : 2,500
    個数       : 1
    商品コード : 000000000002
注文合計金額 : 12,500
-----------------------------
(以下省略)
```
