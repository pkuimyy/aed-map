import requests
import json
import sqlite3
import logging
import datetime
from time import sleep
from tqdm import tqdm
from math import ceil

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
        self.result_file_path = "./data/shenzhen-poi-result.tsv"
        self.db_conn = None
        self.sleep_time = 1.2
        self.item_per_page = 20

        self.base_url = "https://restapi.amap.com/v3/place/text"

        self.url_params = {
            "key": None,
            "types": None,
            "city": None,
            "citylimit": True,
            "offset": 20,
            "page": 1,
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
        count = None
        try:
            req = requests.get(self.base_url, params=url_params)
            req_json = req.json()
            info_code = req_json["infocode"]
        except:
            logging.error(f"adcode: {adcode} poi: {poi} request fail")

        if info_code != "10000":
            logging.error(f"adcode: {adcode} poi: {poi} api fail: {info_code}")
        else:
            count = int(req_json["count"])
            logging.info(f"adcode: {adcode} poi: {poi} count: {count}")

        if count is None:
            return range(1, 1)
        else:
            return range(1, ceil(count/20)+1)

    def get_page(self, adcode, poi, page):
        url_params = self.url_params.copy()
        url_params["types"] = poi
        url_params["city"] = adcode
        url_params["page"] = page
        count = None
        try:
            req = requests.get(self.base_url, params=url_params)
            req_json = req.json()
            info_code = req_json["infocode"]
        except:
            logging.error(
                f"adcode: {adcode} poi: {poi} page: {page} request fail")

        if info_code != "10000":
            logging.error(
                f"adcode: {adcode} poi: {poi} page: {page} api fail: {info_code}")
        else:
            count = int(req_json["count"])
            logging.info(
                f"adcode: {adcode} poi: {poi} page: {page} count: {count}")
        self.save_to_db(adcode, poi, page, req_json)
        # self.save_to_file(adcode, poi, page, req_json)

    def save_to_db(self, adcode, poi, page, req):
        table = "main"
        cursor = self.db_conn.cursor()
        req = json.dumps(req, ensure_ascii=False)
        insert_sql = f"insert into {table} (adcode,poi,page,data) values ('{adcode}','{poi}',{page},'{req}')"
        try:
            cursor.execute(insert_sql)
            self.db_conn.commit()
        except:
            logging.error(
                f"adcode: {adcode} poi: {poi} page: {page} save to db fail")
            self.save_to_file(adcode, poi, page, req)

    def save_to_file(self, adcode, poi, page, req):
        req = json.dumps(req, ensure_ascii=False)
        with open(self.result_file_path, encoding="utf-8", mode="a") as f:
            f.write(f"{adcode}\t{poi}\t{page}\t{req}\n")

    def run(self):
        self.load_key()
        self.load_gaode_poi_code()
        self.load_shenzhen_adcode()
        self.connect_db()
        logging.info("outter data load")
        task_list = [(a, p) for a in self.shenzhen_adcode_obj.values()
                     for p in self.gaode_poi_code_obj.values()]
        for adcode, poi in tqdm(task_list, ncols=70):
            sleep(self.sleep_time)
            page_num = self.get_page_num(adcode, poi)
            for page in page_num:
                self.get_page(adcode, poi, page)
        self.db_conn.close()


if __name__ == "__main__":
    g = GaodePoiMap()
    g.run()
