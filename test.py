import requests
import time


def get():
    nowDate = time.strftime("%Y%m%d", time.localtime())
    res = requests.get('https://file1.dxycdn.com/2020/0223/601/3398299749526003726-135.json')
    # print(res.text)
    content = res.json()
    # print(content['data'])
    for i in range(len(content['data']) - 1, -1, -1):
        text = content['data'][i]
        if text['dateId'] == '20210523':
            return text['currentConfirmedIncr'], text['confirmedIncr'], text['curedIncr'], text['deadIncr']
    return 0, 0, 0, 0


def getDanagerLevel(x):
    return {
        1: '高风险地区',
        2: '中风险地区',
        3: '低风险地区'
    }.get(x, '')


if __name__ == '__main__':
    # currentConfirmedIncr, confirmedIncr, curedIncr, deadIncr = get()
    # print(currentConfirmedIncr, confirmedIncr, curedIncr, deadIncr)
    print(getDanagerLevel(2))
