import requests
import json

if __name__ == "__main__":
    with open("./config.json", encoding="utf-8", mode="r") as f:
        key_config = json.load(f)
    key = key_config["tencent-key"]

    test_adcode = 440305
    base_url = "https://apis.map.qq.com/ws/place/v1/search"
    url_params = {
        "keyword": "AED地图",
        "boundary": f"region({test_adcode},0)",
        "page_size": 20,
        "key": f"{key}",
        "page_index": 1,
    }
    r = requests.get(base_url, params=url_params)
    print(r.json())
