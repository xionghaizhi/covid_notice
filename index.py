import json
import re
import requests
import os


def crawl_dxy_data():
    """
    爬取丁香医生实时统计数据，保存到data目录下，以当前日期作为文件名，存JSON文件
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
        url_content = re.search(r'window.getListByCountryTypeService2true = (.*?)}]}catch', url_text, re.S)
        texts = url_content.group()
        content = texts.replace('window.getListByCountryTypeService2true = ', '').replace('}catch', '')
        json_data = json.loads(content)
        create_notice(json_data)
        # with open('data/app-' + today + '.json', 'w', encoding='UTF-8') as f:
        #     json.dump(json_data, f, ensure_ascii=False)
    except Exception as e:
        print("请求或解析数据失败：{}".format(e))


# 解析数据
def crawl_parser_data():
    """
    获取全球国家的名称和确诊数量
    """
    with open('data/app-' + today + '.json', 'r', encoding='UTF-8') as file:
        json_array = json.loads(file.read())

    county_lists = []  # [provinceName,confirmedCount]
    for province in json_array:
        provinceName = province.get("provinceName")
        confirmedCount = province.get("confirmedCount")
        if provinceName and confirmedCount:
            county_lists.append([provinceName, confirmedCount])
    print(county_lists)
    return county_lists


# 制作地图
def create_map(county_lists):
    # 自定义的每一段的范围，以及每一段的特别的样式。
    pieces = [
        {'min': 10000000, 'color': '#540d0d'},
        {'max': 9999999, 'min': 1000000, 'color': '#9c1414'},
        {'max': 999999, 'min': 100000, 'color': '#d92727'},
        {'max': 99999, 'min': 10000, 'color': '#ed3232'},
        {'max': 9999, 'min': 1000, 'color': '#f27777'},
        {'max': 999, 'min': 1, 'color': '#f7adad'},
        {'max': 0, 'color': '#f7e4e4'},
    ]
    # map由于传入的国家名字需要英文，所以还得转换下,这里需要注意：英文名字必须和地图显示的要一样，所以这里比较花时间，理了很长时间
    POPULATION = [['China', '中国'], ['India', '印度'], ['United States', '美国'], ['Indonesia', '印度尼西亚'], ['Brazil', '巴西'],
                  ['Pakistan', '巴基斯坦'], ['Nigeria', '尼日利亚'], ['Bangladesh', '孟加拉国'], ['Russia', '俄罗斯'],
                  ['Mexico', '墨西哥'], ['Japan', '日本'], ['Ethiopia', '埃塞俄比亚'], ['Philippines', '菲律宾'], ['Egypt', '埃及'],
                  ['Vietnam', '越南'], ['Dem. Rep. Congo', '刚果（布）'], ['Turkey', '土耳其'], ['Iran', '伊朗'], ['Germany', '德国'],
                  ['Thailand', '泰国'], ['United Kingdom', '英国'], ['France', '法国'], ['Tanzania', '坦桑尼亚'],
                  ['Italy', '意大利'], ['South Africa', '南非'], ['Myanmar', '缅甸'], ['Kenya', '肯尼亚'], ['Korea', '韩国'],
                  ['Colombia', '哥伦比亚'], ['Spain', '西班牙'], ['Uganda', '乌干达'], ['Argentina', '阿根廷'], ['Ukraine', '乌克兰'],
                  ['Algeria', '阿尔及利亚'], ['Sudan', '苏丹'], ['Iraq', '伊拉克'], ['Poland', '波兰'], ['Canada', '加拿大'],
                  ['Afghanistan', '阿富汗'], ['Morocco', '摩洛哥'], ['Saudi Arabia', '沙特阿拉伯'], ['Peru', '秘鲁'],
                  ['Uzbekistan', '乌兹别克斯坦'], ['Venezuela', '委内瑞拉'], ['Malaysia', '马来西亚'], ['Angola', '安哥拉'],
                  ['Mozambique', '莫桑比克'], ['Ghana', '加纳'], ['Nepal', '尼泊尔(Never Ever Part As Lovers)'],
                  ['Yemen', '也门共和国'], ['Madagascar', '马达加斯加'], ['Dem. Dep. Korea', '朝鲜'], ["Côte d'Ivoire", '科特迪瓦'],
                  ['Cameroon', '喀麦隆'], ['Australia', '澳大利亚'], ['Taiwan', '中国台湾'], ['Niger', '尼日尔'],
                  ['Sri Lanka', '斯里兰卡'], ['Burkina Faso', '布基纳法索'], ['Malawi', '马拉维'], ['Mali', '马里'],
                  ['Romania', '罗马尼亚'], ['Kazakhstan', '哈萨克斯坦'], ['Syria', '叙利亚'], ['Chile', '智利'], ['Zambia', '赞比亚共和国'],
                  ['Guatemala', '危地马拉'], ['Zimbabwe', '津巴布韦'], ['Netherlands', '荷兰'], ['Ecuador', '厄瓜多尔'],
                  ['Senegal', '塞内加尔'], ['Cambodia', '柬埔寨'], ['Chad', '乍得'], ['Somalia', '索马里'], ['Guinea', '几内亚'],
                  ['S. Sudan', '南苏丹'], ['Rwanda', '卢旺达'], ['Benin', '贝宁'], ['Tunisia', '突尼斯'], ['Burundi', '布隆迪共和国'],
                  ['Belgium', '比利时'], ['Cuba', '古巴'], ['Bolivia', '玻利维亚'], ['Haiti', '海地'], ['Greece', '希腊'],
                  ['Dominican Rep.', '多米尼加'], ['Czechia', '捷克'], ['Portugal', '葡萄牙'], ['Jordan', '约旦'],
                  ['Sweden', '瑞典'], ['Azerbaijan', '阿塞拜疆'], ['United Arab Emirates', '阿拉伯联合酋长国'], ['Hungary', '匈牙利'],
                  ['Honduras', '洪都拉斯'], ['Belarus', '白俄罗斯'], ['Tajikistan', '塔吉克斯坦'], ['Austria', '奥地利'],
                  ['Serbia', '塞尔维亚'], ['Switzerland', '瑞士'], ['Papua New Guinea', '巴布亚新几内亚'], ['Israel', '以色列'],
                  ['Togo', '多哥'], ['Sierra Leone', '塞拉利昂'], ['Hong Kong', '中国香港'], ['Laos', '老挝'], ['Bulgaria', '保加利亚'],
                  ['Paraguay', '巴拉圭'], ['Libya', '利比亚'], ['El Salvador', '萨尔瓦多'], ['Nicaragua', '尼加拉瓜'],
                  ['Kyrgyzstan', '吉尔吉斯斯坦'], ['Lebanon', '黎巴嫩'], ['Turkmenistan', '土库曼斯坦'], ['Singapore', '新加坡'],
                  ['Denmark', '丹麦'], ['Finland', '芬兰'], ['Congo', '刚果（金）'], ['Slovakia', '斯洛伐克'], ['Norway', '挪威'],
                  ['Eritrea', '厄立特里亚'], ['State of Palestine', '巴勒斯坦国'], ['Oman', '阿曼'], ['Costa Rica', '哥斯达黎加'],
                  ['Liberia', '利比里亚'], ['Ireland', '爱尔兰'], ['Central African Rep.', '中非共和国'],
                  ['New Zealand', '新西兰'], ['Mauritania', '毛里塔尼亚'], ['Kuwait', '科威特'], ['Panama', '巴拿马'],
                  ['Croatia', '克罗地亚'], ['Moldova', '摩尔多瓦'], ['Georgia', '格鲁吉亚'], ['Puerto Rico', '波多黎各'],
                  ['Bosnia and Herzegovina', '波斯尼亚和黑塞哥维那'], ['Uruguay', '乌拉圭'], ['Mongolia', '蒙古'],
                  ['Albania', '阿尔巴尼亚'], ['Armenia', '亚美尼亚'], ['Jamaica', '牙买加'], ['Lithuania', '立陶宛'], ['Qatar', '卡塔尔'],
                  ['Namibia', '纳米比亚'], ['Botswana', '博茨瓦纳'], ['Lesotho', '莱索托'], ['Gambia', '冈比亚'], ['Gabon', '加蓬'],
                  ['North Macedonia', '北马其顿'], ['Slovenia', '斯洛文尼亚'], ['Guinea-Bissau', '几内亚比绍'], ['Latvia', '拉脱维亚'],
                  ['Bahrain', ['巴林']], ['Swaziland', '史瓦济兰'], ['Trinidad and Tobago', '特立尼达和多巴哥'],
                  ['Equatorial Guinea', '赤道几内亚'], ['Timor-Leste', '东帝汶'], ['Estonia', '爱沙尼亚'], ['Mauritius', '毛里求斯'],
                  ['Cyprus', '塞浦路斯'], ['Djibouti', '吉布提'], ['Fiji', '斐济'], ['Réunion', '留尼汪'], ['Comoros', '科摩罗'],
                  ['Bhutan', '不丹'], ['Guyana', '圭亚那'], ['Macao', '澳门日报'], ['Solomon Islands', '所罗门群岛'],
                  ['Montenegro', '黑山'], ['Luxembourg', '卢森堡'], ['W. Sahara', '西撒哈拉'], ['Suriname', '苏里南'],
                  ['Cabo Verde', '佛得角'], ['Micronesia', '密克罗尼西亚'], ['Maldives', '马尔代夫'], ['Guadeloupe', '瓜德罗普'],
                  ['Brunei', '文莱'], ['Malta', '马耳他'], ['Bahamas', '巴哈马'], ['Belize', '伯利兹'], ['Martinique', '马提尼克'],
                  ['Iceland', '冰岛'], ['French Guiana', '法属圭亚那'], ['French Polynesia', '法属波利尼西亚'], ['Vanuatu', '瓦努阿图'],
                  ['Barbados', '巴巴多斯'], ['New Caledonia', '新喀里多尼亚'], ['Mayotte', '马约特'],
                  ['Sao Tome & Principe', '圣多美和普林西比'], ['Samoa', '萨摩亚'], ['Saint Lucia', '圣卢西亚'], ['Guam', '关岛'],
                  ['Channel Islands', '海峡群岛'], ['Curaçao', '库拉索'], ['Kiribati', '基里巴斯'],
                  ['St. Vincent & Grenadines', '圣文森特和格林纳丁斯'], ['Tonga', '汤加'], ['Grenada', '格林纳达'], ['Aruba', '阿鲁巴'],
                  ['U.S. Virgin Islands', ['美属维尔京群岛']], ['Antigua and Barbuda', '安提瓜和巴布达'], ['Seychelles', '塞舌尔'],
                  ['Isle of Man', '马恩岛'], ['Andorra', '安道尔'], ['Dominica', '多米尼克'], ['Cayman Islands', '开曼群岛'],
                  ['Bermuda', '百慕大'], ['Greenland', '格陵兰'], ['Saint Kitts & Nevis', '圣基茨和尼维斯'],
                  ['American Samoa', '东萨摩亚'], ['Northern Mariana Islands', '北马里亚纳群岛'], ['Marshall Islands', '马绍尔群岛'],
                  ['Faeroe Islands', '法罗群岛'], ['Sint Maarten', '荷属圣马丁'], ['Monaco', '摩纳哥公国'],
                  ['Liechtenstein', '列支敦斯登'], ['Turks and Caicos', '特克斯和凯科斯群岛'], ['Gibraltar', '直布罗陀'],
                  ['San Marino', '圣马力诺'], ['British Virgin Islands', '英属维尔京群岛'], ['Caribbean Netherlands', '荷兰加勒比区'],
                  ['Palau', '帕劳'], ['Cook Islands', '库克群岛'], ['Anguilla', '安圭拉'], ['Wallis & Futuna', '沃利斯群岛'],
                  ['Tuvalu', '吐瓦鲁'], ['Nauru', '鲁岛'], ['Saint Pierre & Miquelon', '圣皮埃尔'], ['Montserrat', '蒙塞拉特'],
                  ['Saint Helena', '圣赫勒拿岛'], ['Falkland Islands', '福克兰'], ['Niue', '纽埃'], ['Tokelau', '托克劳群岛'],
                  ['Holy See', '圣座']]

    country_data = []
    for p in POPULATION:
        for c in county_lists:
            if c[0] == p[1]:
                country_data.append([p[0], c[1]])
                break
    # print(country_data)
    # print(county_lists)
    from pyecharts.charts import Map
    m = Map()
    m.add("累计确诊", country_data, "world")
    m.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    m.set_global_opts(
        title_opts=opts.TitleOpts(title='全球实时确诊数据',
                                  subtitle='数据来源：丁香园'),
        legend_opts=opts.LegendOpts(is_show=False),
        visualmap_opts=opts.VisualMapOpts(pieces=pieces,
                                          is_piecewise=True,  # 是否为分段型
                                          is_show=True))  # 是否显示视觉映射配置
    m.render("data/map_world.html")


def create_notice(json_array):
    # with open('data/app-' + today + '.json', 'r', encoding='UTF-8') as file:
    #     json_array = json.loads(file.read())
    notice = ''
    for item in json_array:
        if item['provinceName'] in os.environ["AREA_LIST"]:
            temp = f'地区：{item["provinceName"]} \n' \
                   f'现存确诊：{item["currentConfirmedCount"]}，昨日新增：{getDataNumber(item, "currentConfirmedIncr")} \n' \
                   f'累计确诊：{item["confirmedCount"]}，昨日累计确诊新增：{getDataNumber(item, "confirmedIncr")} \n' \
                   f'累计治愈：{item["curedCount"]}，昨日治愈新增：{getDataNumber(item, "curedIncr")} \n' \
                   f'累计死亡：{item["deadCount"]}，昨日死亡新增：{getDataNumber(item, "deadIncr")} '
            if notice == '':
                notice = temp
            else:
                notice = notice + '\n===================\n' + temp
    sendMsg(notice)


def getDataNumber(item, Keyword):
    if item["incrVo"] is None or item['incrVo'] == {}:
        return '暂无数据'
    return item["incrVo"][Keyword]


def sendMsg(content):
    url = f'http://www.pushplus.plus/send?token={os.environ["PUSHPLUS_TOKEN"]}&title=疫情订阅&content={content}&template=html&topic=COVID'
    requests.get(url)


if __name__ == '__main__':
    crawl_dxy_data()
    # create_notice()
    # county_lists = crawl_parser_data()
    # create_map(county_lists)
