import requests
import json
import sqlite3
import logging
import datetime
from time import sleep
from tqdm import tqdm

now = datetime.datetime.now().strftime(r"%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f"./log/{now}.log",
    level=logging.INFO,
    filemode="a",
    format=r"%(asctime)s - %(levelname)s - %(message)s"
)


class GaodePoiMap:
    def __init__(self):
        self.config_path = "./config.json"
        self.gaode_poi_code_path = "./data/gaode-poi-code.json"
        self.gaode_poi_code_obj = None
        self.shenzhen_adcode_path = "./data/shenzhen-adcode.json"
        self.shenzhen_adcode_obj = None
        self.db_path = "./data/aed-map.db"
        self.db_conn = None
        self.sleep_time = 1

        self.base_url = "https://restapi.amap.com/v3/place/text"

        self.url_params = {
            "key": None,
            "types": None,
            "city": None,
            "citylimit": True,
            "offset": 20,
        }

    def load_key(self):
        with open(self.config_path, encoding="utf-8", mode="r") as f:
            tmp = json.load(f)
        self.url_params["key"] = tmp["gaode-key"]

    def load_gaode_poi_code(self):
        with open(self.gaode_poi_code_path, encoding="utf-8", mode="r") as f:
            self.gaode_poi_code_obj = json.load(f)

    def load_shenzhen_adcode(self):
        with open(self.shenzhen_adcode_path, encoding="utf-8", mode="r") as f:
            self.shenzhen_adcode_obj = json.load(f)

    def connect_db(self):
        self.db_conn = sqlite3.connect(self.db_path)

    def get_page_num(self, adcode, poi):
        url_params = self.url_params.copy()
        url_params["types"] = poi
        url_params["city"] = adcode
        page_num = None
        try:
            req = requests.get(self.base_url, params=url_params)
            req_json = req.json()
            info_code = req_json["infocode"]
            if info_code != "10000":
                logging.error(f"gaode api fail: {info_code}")
            else:
                page_num = req_json["count"]
                logging.info(
                    f"adcode: {adcode} poi: {poi}  page_num: {page_num}")
        except:
            logging.error("request fail")
        return page_num

    def save_to_db(self, adcode, poi, page, req):
        cursor = self.db_conn.cursor()
        req = json.dumps(req, ensure_ascii=False)
        insert_sql = f"insert into test (adcode,poi,page,data) values ('{adcode}','{poi}',{page},'{req}')"
        print(insert_sql)
        cursor.execute(insert_sql)
        self.db_conn.commit()

    def run(self):
        self.load_key()
        self.load_gaode_poi_code()
        self.load_shenzhen_adcode()
        self.connect_db()
        logging.info("adcode and poi code load")
        task_list = [(a, p) for a in self.shenzhen_adcode_obj.values()
                     for p in self.gaode_poi_code_obj.values()]
        page_num_list = []
        # for adcode, poi in tqdm(task_list, ncols=70):
        #     sleep(self.sleep_time)
        #     page_num = self.get_page_num(adcode, poi)
        with open("./tmp.json", encoding="utf-8", mode="r") as f:
            tmp_req = json.load(f)
        self.save_to_db("a1", "p1", "-1", tmp_req)
        self.db_conn.close()


if __name__ == "__main__":
    g = GaodePoiMap()
    g.run()
