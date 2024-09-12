# モジュール読み込み
import MakeShopApiMod as msmod
from datetime import datetime, timezone, timedelta
import json
import re
import mkdir_datetime
import csv

# タイムゾーン指定
jst = timezone(timedelta(hours=9), 'JST')

# 設定ファイルから設定情報を読み込み
configData = msmod.readConfigIni('MakeShop.ini')

# 検索条件設定
searchInfo = msmod.readSearchOrderConfigIni('MakeShop.ini')

# 注文履歴を検索
orderJsonList = msmod.searchOrder(configData,searchInfo)

# 注文情報を表示
fileName = 'order_'+mkdir_datetime.get_today_date('')+'_'+mkdir_datetime.get_now_time('')+'.csv'
with open(fileName, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        '注文番号',
        '会員ID(注文番号)',
        '日付',
        '商品名',
        '商品コード',
        '個数',
        '商品価格',
        '支払金額',
        '注文年月',
        '実行日時',
        ])
    
    for orderJson in orderJsonList:
        for orderInfo in orderJson['data']['searchOrder']['orders']:
            sumPrice = 0
            print('-----------------------------')
            print('注文番号 : ' + orderInfo['displayOrderNumber'])
            print('会員ID   : ' + orderInfo['memberId'])
            print('日付     : ' + orderInfo['orderDate'])
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
                    writer.writerow([
                        orderInfo['displayOrderNumber'],  # '注文番号',
                        orderInfo['memberId'],            # '会員ID',
                        orderInfo['orderDate'],           # '日付',
                        basketInfo['productName'],        # '商品名',
                        basketInfo['productCode'],        # '商品コード',
                        basketInfo['amount'],             # '個数',
                        basketInfo['price'],              # '商品価格',
                        orderInfo['sumPrice'],            # '支払金額',
                        orderYearMonth,                   # '注文年月',
                        mkdir_datetime.get_today_date('-')+' '+mkdir_datetime.get_now_time(),        # '実行日時',
                        ])
            print('注文合計金額 : ' + '{:,}'.format(sumPrice))


