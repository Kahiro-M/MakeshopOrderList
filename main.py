# モジュール読み込み
import MakeShopApiMod as msmod
from datetime import datetime, timezone, timedelta
import json
jst = timezone(timedelta(hours=9), 'JST')

# 設定ファイルから設定情報を読み込み
configData = msmod.readConfigIni('MakeShop.ini')

# 検索条件設定
searchInfo = {'deliveryStatus':'Y','sortOrder':'ASC','page':1,'limit':2}

# 注文履歴を検索
orderJsonList = msmod.searchOrder(configData,searchInfo)

# 注文情報を表示
for orderJson in orderJsonList:
    for orderInfo in orderJson['data']['searchOrder']['orders']:
        print('-----------------------------')
        print('注文番号 : ' + orderInfo['displayOrderNumber'])
        print('会員ID   : ' + orderInfo['memberId'])
        print('注文日時 : ' + orderInfo['orderDate'])
        datetimeStr = orderInfo['orderDate']
        dt = datetime.strptime(datetimeStr,'%Y-%m-%d %H:%M:%S')
        orderYearMonth = dt.astimezone(jst).strftime('%Y%m')
        print('注文年月 : ' + orderYearMonth)

