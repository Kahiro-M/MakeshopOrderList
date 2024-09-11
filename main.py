# モジュール読み込み
import MakeShopApiMod as msmod
from datetime import datetime, timezone, timedelta
import json
import re
jst = timezone(timedelta(hours=9), 'JST')

# 設定ファイルから設定情報を読み込み
configData = msmod.readConfigIni('MakeShop.ini')

# 検索条件設定
searchInfo = msmod.readSearchOrderConfigIni('MakeShop.ini')

# 注文履歴を検索
orderJsonList = msmod.searchOrder(configData,searchInfo)

# 注文情報を表示
for orderJson in orderJsonList:
    for orderInfo in orderJson['data']['searchOrder']['orders']:
        sumPrice = 0
        print('-----------------------------')
        print('注文番号 : ' + orderInfo['displayOrderNumber'])
        print('会員ID   : ' + orderInfo['memberId'])
        print('注文日時 : ' + orderInfo['orderDate'])
        datetimeStr = orderInfo['orderDate']
        dt = datetime.strptime(datetimeStr,'%Y-%m-%d %H:%M:%S')
        orderYearMonth = dt.astimezone(jst).strftime('%Y%m')
        print('注文年月 : ' + orderYearMonth)
        i = 1
        for basketInfo in orderInfo['deliveryInfos'][0]['basketInfos']:
            # iniで設定された検索条件の商品名（正規表現）に合致する注文情報だけ抽出
            if(len(re.findall(searchInfo['PRODUCT_NAME'],basketInfo['productName']))>0):
                print('  商品名' + str(i))
                print('    商品名     : ' + basketInfo['productName'])
                print('    商品価格   : ' + '{:,}'.format(basketInfo['price']))
                print('    個数       : ' + '{:,}'.format(basketInfo['amount']))
                print('    商品コード : ' + basketInfo['productCode'])
                i += 1
                sumPrice += basketInfo['price'] * basketInfo['amount']
        print('注文合計金額 : ' + '{:,}'.format(sumPrice))

