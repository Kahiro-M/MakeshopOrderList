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
        return {'type':'error','hasOptions':config.options(str(appId))}



# アーカイブされた取引先情報を取得
def searchOrder(config,searchInfo={'deliveryStatus':'Y','sortOrder':'ASC','page':1,'limit':1000}):
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

    if(searchInfo['deliveryStatus'] not in ['N','Y','C','R']):
        searchInfo['deliveryStatus'] = 'Y'
    if(searchInfo['sortOrder'] not in ['ASC','DESC']):
        searchInfo['sortOrder'] = 'ASC'
    if(searchInfo['page'] < 1):
        searchInfo['page'] = 1
    if(searchInfo['limit'] > 1000 or searchInfo['limit'] < 1):
        searchInfo['limit'] = 1000
    
    json_data = {
        'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {displayOrderNumber orderDate memberId sumPrice deliveryInfos {basketInfos {productName price}}}}}',
        'variables': {
            'input': {
                'deliveryStatus':searchInfo['deliveryStatus'],
                'sortOrder':searchInfo['sortOrder'],
                'page':searchInfo['page'],
                'limit':searchInfo['limit'],
            },
        },
    }
    response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
    res = []
    res.append(response.json())
    
    count = res[0]['data']['searchOrder']['searchedCount']
    i = 1
    while(count > searchInfo['limit']):
        json_data = {
            'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {displayOrderNumber orderDate memberId sumPrice deliveryInfos {basketInfos {productName price}}}}}',
            'variables': {
                'input': {
                    'deliveryStatus':searchInfo['deliveryStatus'],
                    'sortOrder':searchInfo['sortOrder'],
                    'page':searchInfo['page']+i,
                    'limit':searchInfo['limit'],
                },
            },
        }
        response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
        res.append(response.json())
        count -= searchInfo['limit']
        i += 1
    return res
