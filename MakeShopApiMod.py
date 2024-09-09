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

    #設定情報取得
    if(config.has_option('SearchOrder','DELIVERY_STATUS')
        and config.has_option('SearchOrder','SORT_ORDER')
        and config.has_option('SearchOrder','PAGE')
        and config.has_option('SearchOrder','LIMIT')
    ):
        ConfigData = {
            'DELIVERY_STATUS' : config.get('SearchOrder','DELIVERY_STATUS'),
            'SORT_ORDER'      : config.get('SearchOrder','SORT_ORDER'),
            'PAGE'            : int(config.get('SearchOrder','PAGE')),
            'LIMIT'           : int(config.get('SearchOrder','LIMIT')),
        }
        return ConfigData
    else:
        return {'type':'error','hasOptions':config.options('SearchOrder')}



# アーカイブされた取引先情報を取得
def searchOrder(config,searchInfo):
    import requests
    import json
    import time
    import math
    
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
    
    # APIのRequest作成
    json_data = {
        'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {displayOrderNumber orderDate memberId sumPrice deliveryInfos {basketInfos {productName price}}}}}',
        'variables': {
            'input': {
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
