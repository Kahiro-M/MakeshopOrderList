# -------------------------------------------------- # 
# MakeShop REST API モジュール 
# -------------------------------------------------- #   



# iniファイルから設定を読み込む
def readConfigIni(filePath='MakeShop.ini'):
    import configparser

    #ConfigParserオブジェクトを生成
    config = configparser.ConfigParser()

    #設定ファイル読み込み
    config.read(filePath,encoding='utf8')

    #設定情報取得
    if(config.has_option('MakeShop','TOKEN')
        and config.has_option('MakeShop','END_POINT')
        and config.has_option('MakeShop','API_KEY')
        and config.has_option('MakeShop','SECRET_KEY')
    ):
        ConfigData = {
            'TOKEN'      : config.get('MakeShop','TOKEN'),
            'END_POINT'  : config.get('MakeShop','END_POINT'),
            'API_KEY'    : config.get('MakeShop','API_KEY'),
            'SECRET_KEY' : config.get('MakeShop','SECRET_KEY'),
        }
        return ConfigData
    else:
        return {'type':'error','hasOptions':config.options('MakeShop')}



# iniファイルから検索条件設定を読み込む
def readSearchOrderConfigIni(filePath='MakeShop.ini'):
    import configparser

    #ConfigParserオブジェクトを生成
    config = configparser.ConfigParser()

    #設定ファイル読み込み
    config.read(filePath,encoding='utf8')

    ConfigData = {}

    #設定情報取得
    if(config.has_option('SearchOrder','DELIVERY_STATUS')):
        ConfigData['DELIVERY_STATUS'] = config.get('SearchOrder','DELIVERY_STATUS')
    else:
        ConfigData['DELIVERY_STATUS'] = 'Y'

    if(config.has_option('SearchOrder','SORT_ORDER')):
        ConfigData['SORT_ORDER'] = config.get('SearchOrder','SORT_ORDER')
    else:
        ConfigData['SORT_ORDER'] = 'ASC'

    if(config.has_option('SearchOrder','PAGE')):
        ConfigData['PAGE'] = int(config.get('SearchOrder','PAGE'))
    else:
        ConfigData['PAGE'] = 1

    if(config.has_option('SearchOrder','LIMIT')):
        ConfigData['LIMIT'] = int(config.get('SearchOrder','LIMIT'))
    else:
        ConfigData['LIMIT'] = 1000

    if(config.has_option('SearchOrder','PRODUCT_NAME')):
        ConfigData['PRODUCT_NAME'] = config.get('SearchOrder','PRODUCT_NAME')
    else:
        ConfigData['PRODUCT_NAME'] = '.*'

    if(config.has_option('SearchOrder','START_DATE')):
        ConfigData['START_DATE'] = config.get('SearchOrder','START_DATE')
    else:
        ConfigData['START_DATE'] = '1970-01-01 00:00:00'

    if(config.has_option('SearchOrder','END_DATE')):
        ConfigData['END_DATE'] = config.get('SearchOrder','END_DATE')
    else:
        ConfigData['END_DATE'] = '9999-12-31 23:59:59'

    return ConfigData



# iniファイルから検索条件設定を読み込む
def readParamConfigIni(optionName,filePath='MakeShop.ini'):
    import configparser

    #ConfigParserオブジェクトを生成
    config = configparser.ConfigParser()

    #設定ファイル読み込み
    config.read(filePath,encoding='utf8')

    #設定情報取得
    if(config.has_option(optionName,'PARAM')):
        ConfigData = {
            'PARAM' : config.get(optionName,'PARAM'),
        }
        return eval(ConfigData['PARAM'])
    else:
        return {'type':'error','hasOptions':config.options(optionName)}



# アーカイブされた取引先情報を取得
def searchOrder(config,searchInfo):
    import requests
    import json
    import time
    import math
    from datetime import datetime, timedelta

    # UNIX時間
    ut = time.time()

    header_data = {
        'authorization': 'Bearer '+config['TOKEN'],
        'content-type': 'application/json',
        'x-api-key': config['API_KEY'],
        'x-timestamp': str(math.floor(ut)),
    }

    # 検索条件の正規化
    if(searchInfo['DELIVERY_STATUS'] not in ['N','Y','C','R']):
        searchInfo['DELIVERY_STATUS'] = 'Y'
    if(searchInfo['SORT_ORDER'] not in ['ASC','DESC']):
        searchInfo['SORT_ORDER'] = 'ASC'
    if(searchInfo['PAGE'] < 1):
        searchInfo['PAGE'] = 1
    if(searchInfo['LIMIT'] > 1000 or searchInfo['LIMIT'] < 1):
        searchInfo['LIMIT'] = 1000
    try:
        date_object = datetime.strptime(searchInfo['START_DATE'], "%Y-%m-%d %H:%M:%S")
        searchInfo['START_DATE'] = date_object.strftime('%Y%m%d%H%M%S')
    except ValueError:
        searchInfo['START_DATE'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        date_object = datetime.strptime(searchInfo['END_DATE'], "%Y-%m-%d %H:%M:%S")
        searchInfo['END_DATE'] = date_object.strftime('%Y%m%d%H%M%S')
    except ValueError:
        searchInfo['END_DATE'] = (datetime.now()-timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        
    
    basketInfos = [
        'productName', # 商品名
        'price', # 商品価格
        'amount', # 個数
        'productCode', # 商品コード
    ]
    basketInfosStr = 'basketInfos {'+' '.join(basketInfos)+'}'
    deliveryInfosStr = 'deliveryInfos {'+basketInfosStr+'}'

    searchedOrderInfo = [
        'memberId', # 会員ID(注文番号)
        'orderDate', # 日付
        'sumPrice', # 支払金額
        'senderPrefecture', # 注文者の住所（都道府県）
        'displayOrderNumber', # 注文番号
    ]
    searchedOrderInfoStr = ' '.join(searchedOrderInfo)

    # APIのRequest作成
    json_data = {
        'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {'+searchedOrderInfoStr+' '+deliveryInfosStr+'}}}',
        'variables': {
            'input': {
                'startOrderDate':searchInfo['START_DATE'],
                'endOrderDate':searchInfo['END_DATE'],
                'deliveryStatus':searchInfo['DELIVERY_STATUS'],
                'sortOrder':searchInfo['SORT_ORDER'],
                'page':searchInfo['PAGE'],
                'limit':searchInfo['LIMIT'],
            },
        },
    }

    # 結果の保存
    response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
    res = []
    res.append(response.json())
    
    # 検索結果が2ページ以上の場合
    count = res[0]['data']['searchOrder']['searchedCount']
    i = 1
    while(count > searchInfo['LIMIT']):
        json_data = {
            'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {displayOrderNumber orderDate memberId sumPrice deliveryInfos {basketInfos {productName price}}}}}',
            'variables': {
                'input': {
                    'startOrderDate':searchInfo['START_DATE'],
                    'endOrderDate':searchInfo['END_DATE'],
                    'deliveryStatus':searchInfo['DELIVERY_STATUS'],
                    'sortOrder':searchInfo['SORT_ORDER'],
                    'page':searchInfo['PAGE']+i,
                    'limit':searchInfo['LIMIT'],
                },
            },
        }
        response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
        res.append(response.json())
        count -= searchInfo['LIMIT']
        i += 1

    return res
