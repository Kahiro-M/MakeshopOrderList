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

# 会員所属グループLUT
memberJsonList = msmod.searchMember(configData,searchInfo)
MEMBER_ID_TO_GROUP_NAME = {}
for memberInfo in memberJsonList[0]['data']['searchMember']['members']:
    MEMBER_ID_TO_GROUP_NAME[memberInfo['memberId']] = memberInfo['groupName']

# 配送情報LUT
DELIVERY_STATUS_CODE_TO_DELIVERY_STATUS_NAME = msmod.getDeliveryStatusList()


# 注文情報を表示
fileName = 'order_'+mkdir_datetime.get_today_date('')+'_'+mkdir_datetime.get_now_time('')+'.csv'
with open(fileName, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        '注文番号',
        '会員ID(注文番号)',
        '注文者の住所（都道府県）',
        '日付',
        '商品名',
        '商品コード',
        '個数',
        '商品価格',
        '支払金額',
        'グループ名',
        '処理状況',
        '注文年月',
        '実行日時',
        ])
    
    for orderJson in orderJsonList:
        for orderInfo in orderJson['data']['searchOrder']['orders']:
            sumPrice = 0
            print('-----------------------------')
            print('注文番号 : ' + orderInfo.get('displayOrderNumber',''))
            print('会員ID   : ' + orderInfo.get('memberId',''))
            print('都道府県 : ' + orderInfo.get('senderPrefecture','登録なし'))
            print('日付     : ' + orderInfo.get('orderDate',''))
            datetimeStr = orderInfo.get('orderDate','')
            dt = datetime.strptime(datetimeStr,'%Y-%m-%d %H:%M:%S')
            orderYearMonth = dt.astimezone(jst).strftime('%Y%m')
            print('注文年月 : ' + orderYearMonth)
            groupName = MEMBER_ID_TO_GROUP_NAME.get(orderInfo.get('memberId',''),'')
            print('グループ : ' + groupName)
            deliveryStatus = DELIVERY_STATUS_CODE_TO_DELIVERY_STATUS_NAME[searchInfo['DELIVERY_STATUS']]
            print('処理状況 : ' + deliveryStatus)
            i = 1
            for basketInfo in orderInfo['deliveryInfos'][0]['basketInfos']:
                # iniで設定された検索条件の商品名（正規表現）に合致する注文情報だけ抽出
                if(
                    len(re.findall(searchInfo['PRODUCT_NAME'],basketInfo['productName']))>0
                    and len(re.findall(searchInfo['GROUP_NAME'],groupName))>0
                ):
                    print('  商品名' + str(i))
                    print('    商品名     : ' + basketInfo.get('productName',''))
                    print('    商品価格   : ' + '{:,}'.format(basketInfo.get('price',0)))
                    print('    個数       : ' + '{:,}'.format(basketInfo.get('amount',0)))
                    print('    商品コード : ' + basketInfo.get('productCode',''))
                    i += 1
                    sumPrice += basketInfo.get('price',0) * basketInfo.get('amount',0)
                    writer.writerow([
                        orderInfo.get('displayOrderNumber',''),       # '注文番号',
                        orderInfo.get('memberId',''),                 # '会員ID',
                        orderInfo.get('senderPrefecture','登録なし'), # '都道府県',
                        orderInfo.get('orderDate',''),                # '日付',
                        basketInfo.get('productName',''),             # '商品名',
                        basketInfo.get('productCode',''),             # '商品コード',
                        basketInfo.get('amount','0'),                 # '個数',
                        basketInfo.get('price','0'),                  # '商品価格',
                        orderInfo.get('sumPrice','0'),                # '支払金額',
                        groupName,                                    # 'グループ名',
                        deliveryStatus,                               # '処理状況',
                        orderYearMonth,                               # '注文年月',
                        mkdir_datetime.get_today_date('-')+' '+mkdir_datetime.get_now_time(),        # '実行日時',
                        ])
            print('注文合計金額 : ' + '{:,}'.format(sumPrice))


