import json
import re
import requests
import os


def crawl_dxy_data():
    """
    爬取丁香医生实时统计数据
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; TAS-AN00 Build/TAS-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 dxyapp_name/aspirin dxyapp_version/8.6.1 dxyapp_system_version/5.1.1 dxyapp_client_id/19a3d982dedd4da4bda7e303992bffe3 dxyapp_ac/d5424fa6-adff-4b0a-8917-4264daf4a348 dxyapp_sid/47121485-cea5-4144-80a8-8ecda8510946"
    }
    try:
        response = requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia',
                                headers=headers)
        response.encoding = response.apparent_encoding
        url_text = response.text
        # print(url_text)
        # 国际数据
        url_country_content = re.search(r'window.getListByCountryTypeService2true = (.*?)}]}catch', url_text, re.S)
        texts = url_country_content.group()
        content_country = texts.replace('window.getListByCountryTypeService2true = ', '').replace('}catch', '')
        json_data_country = json.loads(content_country)
        # 国内数据
        url_area_content = re.search(r'window.getAreaStat = (.*?)}]}catch', url_text, re.S)
        texts_area = url_area_content.group()
        content_area = texts_area.replace('window.getAreaStat = ', '').replace('}catch', '')
        json_data_area = json.loads(content_area)

        # print(json_data_area)
        # print(json_data_country)
        return json_data_country, json_data_area
    except Exception as e:
        print("请求或解析数据失败：{}".format(e))


def getDataNumber(item, Keyword):
    '''解析数据'''
    if item["incrVo"] is None or item['incrVo'] == {}:
        return '暂无数据'
    return item["incrVo"][Keyword]


def sendMsg(content):
    '''发送数据'''
    url = f'http://www.pushplus.plus/send?token={os.environ["PUSHPLUS_TOKEN"]}&title=疫情订阅&content={content}&template=markdown&topic=COVID'
    requests.get(url)


def getCountryData(data, searchData):
    '''获取国家信息'''
    for item in data:
        if searchData in item['provinceName'] or searchData == item['locationId']:
            temp = f' - 地区：**{item["provinceName"]}** \n' \
                   f'> * 现存确诊：{item["currentConfirmedCount"]}，较昨日新增：{getDataNumber(item, "currentConfirmedIncr")} \n' \
                   f'> * 累计确诊：{item["confirmedCount"]}，较昨日累计确诊新增：{getDataNumber(item, "confirmedIncr")} \n' \
                   f'> * 累计治愈：{item["curedCount"]}，较昨日治愈新增：{getDataNumber(item, "curedIncr")} \n' \
                   f'> * 累计死亡：{item["deadCount"]}，较昨日死亡新增：{getDataNumber(item, "deadIncr")} \n\n'
            return temp
    return '暂无数据'


def getProvinceData(data, searchData):
    '''获取省份信息'''
    for item in data:
        if searchData in item['provinceName'] or searchData == item['locationId']:
            # 获取静态文件
            currentConfirmedIncr, confirmedIncr, curedIncr, deadIncr = getVariable(item['statisticsData'])
            temp = f' - 地区：**{item["provinceName"]}** \n' \
                   f'> * 现存确诊：{item["currentConfirmedCount"]}，较昨日新增：{currentConfirmedIncr} \n' \
                   f'> * 累计确诊：{item["confirmedCount"]}，较昨日累计确诊新增：{confirmedIncr} \n' \
                   f'> * 累计治愈：{item["curedCount"]}，较昨日治愈新增：{curedIncr} \n' \
                   f'> * 累计死亡：{item["deadCount"]}，较昨日死亡新增：{deadIncr} \n' \
                   f'> * 疑似数量：{item["suspectedCount"]} \n\n'
            return temp
    return '暂无数据'


def getCityData(data, searchData):
    '''获取城市信息'''
    for item in data:
        for city_item in item['cities']:
            if searchData in city_item['cityName'] or searchData == city_item['locationId']:
                # 获取静态文件
                temp = f' - 地区：**{city_item["cityName"]}** \n' \
                       f'> * 现存确诊：{city_item["currentConfirmedCount"]} \n' \
                       f'> * 累计确诊：{city_item["confirmedCount"]} \n' \
                       f'> * 累计治愈：{city_item["curedCount"]} \n' \
                       f'> * 累计死亡：{city_item["deadCount"]} \n' \
                       f'> * 疑似数量：{city_item["suspectedCount"]}\n\n'
                return temp
    return '暂无数据'


def getNameOrLocationId(data):
    '''获取地区名称或locationId'''
    if data['locationId'] is not None and data['locationId'] != '':
        return data['locationId']
    if data['name'] is not None and data['name'] != '':
        return data['name']
    return None


def getVariable(url):
    import time
    nowDate = time.strftime("%Y%m%d", time.localtime())
    res = requests.get(url)
    # print(res.text)
    content = res.json()
    # print(content['data'])
    for i in range(len(content['data']) - 1, -1, -1):
        text = content['data'][i]
        if text['dateId'] == nowDate:
            return text['currentConfirmedIncr'], text['confirmedIncr'], text['curedIncr'], text['deadIncr']
    return '暂无数据', '暂无数据', '暂无数据', '暂无数据'


def getNotice(json_country, json_area):
    '''获取通知'''
    send_msg = ''
    # 获取数据
    str = os.environ["AREA_OBJ"]
    for item in json.loads(str):
        if send_msg != '':
            send_msg = send_msg + '\n===================\n'
        # 国家
        country = getNameOrLocationId(item)
        if country is not None:
            temp_courntry_msg = getCountryData(json_country, country)
            if send_msg == '':
                send_msg = temp_courntry_msg
            else:
                send_msg = send_msg + '\n' + temp_courntry_msg
        # 省份
        province = item['province']
        if province is not None and province != []:
            for province_item in province:
                # 搜索省份
                search_province = getNameOrLocationId(province_item)
                if search_province is not None:
                    # 获取疫情数据
                    temp_province_msg = getProvinceData(json_area, search_province)
                    if send_msg == '':
                        send_msg = temp_province_msg
                    else:
                        send_msg = send_msg + '\n' + temp_province_msg
                # 城市
                city = province_item['city']
                if city is not None and city != []:
                    for city_item in city:
                        # 搜索省份
                        search_city = getNameOrLocationId(city_item)
                        if search_city is not None:
                            # 获取疫情数据
                            temp_province_msg = getCityData(json_area, search_city)
                            if send_msg == '':
                                send_msg = temp_province_msg
                            else:
                                send_msg = send_msg + '\n' + temp_province_msg
    # print(send_msg)
    return send_msg


if __name__ == '__main__':
    country, area = crawl_dxy_data()
    msg = getNotice(country, area)
    print(msg)
    sendMsg(msg)
