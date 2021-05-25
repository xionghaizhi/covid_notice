[![COVID-19订阅](https://github.com/xionghaizhi/covid_notice/actions/workflows/main.yml/badge.svg)](https://github.com/xionghaizhi/covid_notice/actions/workflows/main.yml)
  
setting -> 增加两个参数  
PUSHPLUS_TOKEN：PUSHPLUS消息推送token  
AREA_OBJ： 
```json
[
    {
        "name": "中国",
        "locationId": "",
        "province": [
            {
                "name": "山东省",
                "locationId": "",
                "city": [
                    {
                        "name": "济南",
                        "locationId": ""
                    }
                ]
            }
        ]
    },
    {
        "name": "阿联酋",  # 必须
        "locationId": "", # 必须
        "province": []    # 必须
    }
]
```