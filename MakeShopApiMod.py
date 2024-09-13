# -------------------------------------------------- # 
# MakeShop REST API モジュール 
# -------------------------------------------------- #   

# Makeshopの配送状態対応表
# https://developers.makeshop.jp/api/graphql/index.html#definition-SearchOrderRequest
def getDeliveryStatusList():
    return {
        'N':'未処理',
        'Y':'配送',
        'C':'キャンセル',
        'R':'返送',
    }

# Makeshopの都道府県コード対応表
# https://developers.makeshop.jp/api/graphql/index.html#introduction-item-2
def getPrefNameList():
    return {
        1:'北海道',
        2:'青森県',
        3:'岩手県',
        4:'宮城県',
        5:'秋田県',
        6:'山形県',
        7:'福島県',
        8:'茨城県',
        9:'栃木県',
        10:'群馬県',
        11:'埼玉県',
        12:'千葉県',
        13:'東京都',
        14:'東京都',
        15:'神奈川県',
        16:'新潟県',
        17:'富山県',
        18:'石川県',
        19:'福井県',
        20:'山梨県',
        21:'長野県',
        22:'岐阜県',
        23:'静岡県',
        24:'愛知県',
        25:'三重県',
        26:'滋賀県',
        27:'京都府',
        28:'大阪府',
        29:'兵庫県',
        30:'奈良県',
        31:'和歌山県',
        32:'鳥取県',
        33:'島根県',
        34:'岡山県',
        35:'広島県',
        36:'山口県',
        37:'徳島県',
        38:'香川県',
        39:'愛媛県',
        40:'高知県',
        41:'福岡県',
        42:'佐賀県',
        43:'長崎県',
        44:'熊本県',
        45:'大分県',
        46:'宮崎県',
        47:'鹿児島県',
        48:'沖縄県',
        49:'離島部',
        50:'海外',
    }

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



# 注文情報を取得
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
    if(searchInfo['DELIVERY_STATUS'] not in [list(getDeliveryStatusList())]):
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
        
    # https://developers.makeshop.jp/api/graphql/index.html#definition-BasketInfo
    basketInfos = [
        'productName', # 商品名
        'price',       # 商品価格
        'amount',      # 個数
        'productCode', # 商品コード
    ]
    basketInfosStr = 'basketInfos {'+' '.join(basketInfos)+'}'
    deliveryInfosStr = 'deliveryInfos {'+basketInfosStr+'}'

    # https://developers.makeshop.jp/api/graphql/index.html#definition-SearchedOrder
    searchedOrderInfo = [
        'memberId',           # 会員ID(注文番号)
        'orderDate',          # 日付
        'sumPrice',           # 支払金額
        'senderPrefecture',   # 注文者の住所（都道府県）
        'displayOrderNumber', # 注文番号
    ]
    searchedOrderInfoStr = ' '.join(searchedOrderInfo)

    # APIのRequest作成
    # https://developers.makeshop.jp/api/graphql/index.html#query-searchOrder
    json_data = {
        'query': 'query searchOrder($input: SearchOrderRequest!) {searchOrder(input: $input) {searchedCount page orders {'+searchedOrderInfoStr+' '+deliveryInfosStr+'}}}',
        'variables': {
            'input': {
                'startOrderDate':searchInfo['START_DATE'],       # 注文日 検索開始日時
                'endOrderDate':searchInfo['END_DATE'],           # 注文日 検索終了日時
                'deliveryStatus':searchInfo['DELIVERY_STATUS'],  # 配送状態
                'sortOrder':searchInfo['SORT_ORDER'],            # ソート順
                'page':searchInfo['PAGE'],                       # ページ番号
                'limit':searchInfo['LIMIT'],                     # 上限数
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
            'query': 'query searchOrder($input: SearchOrderRequest!){searchOrder(input: $input){searchedCount page orders{displayOrderNumber orderDate memberId sumPrice deliveryInfos{basketInfos{productName price}}}}}',
            'variables': {
                'input': {
                    'startOrderDate':searchInfo['START_DATE'],       # 注文日 検索開始日時
                    'endOrderDate':searchInfo['END_DATE'],           # 注文日 検索終了日時
                    'deliveryStatus':searchInfo['DELIVERY_STATUS'],  # 配送状態
                    'sortOrder':searchInfo['SORT_ORDER'],            # ソート順
                    'page':searchInfo['PAGE']+i,                     # ページ番号
                    'limit':searchInfo['LIMIT'],                     # 上限数
                },
            },
        }
        response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
        res.append(response.json())
        count -= searchInfo['LIMIT']
        i += 1

    return res



# 会員情報を取得
def searchMember(config,searchInfo):
    import requests
    import json
    import time
    import math
    # from datetime import datetime, timedelta

    # UNIX時間
    ut = time.time()

    header_data = {
        'authorization': 'Bearer '+config['TOKEN'],
        'content-type': 'application/json',
        'x-api-key': config['API_KEY'],
        'x-timestamp': str(math.floor(ut)),
    }

    # 検索条件の正規化

    # https://developers.makeshop.jp/api/graphql/index.html#definition-MemberInfo
    searchedMemberInfo = [
        'groupId',     # グループID
        'groupName',   # グループ名
        'memberId',    # 会員ID
        'name',        # 会員氏名
        'haddress1',   # 都道府県コード(自宅)
    ]
    searchedMemberInfoStr = ' '.join(searchedMemberInfo)

    # APIのRequest作成
    # https://developers.makeshop.jp/api/graphql/index.html#query-searchMember
    json_data = {
        'query':'query searchMember($input:SearchMemberRequest!){searchMember(input:$input){searchedCount members{'+searchedMemberInfoStr+'}}}',
        'variables': {
            'input': {
                'page':searchInfo['PAGE'],   # ページ番号
                'limit':searchInfo['LIMIT'], # 上限数
            },
        },
    }

    # 結果の保存
    response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
    res = []
    res.append(response.json())
    
    # 検索結果が2ページ以上の場合
    count = res[0]['data']['searchMember']['searchedCount']
    i = 1
    while(count > searchInfo['LIMIT']):
        json_data = {
            'query':'query searchMember($input:SearchMemberRequest!){searchMember(input:$input){searchedCount members{'+searchedMemberInfoStr+'}}}',
            'variables': {
                'input': {
                    'page':searchInfo['PAGE']+i, # ページ番号
                    'limit':searchInfo['LIMIT'], # 上限数
                },
            },
        }

        response = requests.post(config['END_POINT'],headers=header_data,json=json_data)
        res.append(response.json())
        count -= searchInfo['LIMIT']
        i += 1

    return res
