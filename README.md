# 数据采集

## 深圳市各街道adcode

- https://lbs.amap.com/api/webservice/download
- 简单处理后得到`./data/china-adcode.csv`与`./data/shenzhen-adcode.json`

## 深圳市各街道边界

- 没有现成的数据
- 需要找到较新的深圳街道地图，手工描绘边界。而后转化成geoJson格式

## 深圳市AED地图

- https://lbs.qq.com/service/webService/webServiceGuide/webServiceSearch
- 爬虫思路：
    - 腾讯位置服务API有返回数据数量的上限，为200 https://lbs.qq.com/FAQ/server_faq.html#1
    - 腾讯地图上显示AED共有303个，因此划分深圳市为各个区分别发送请求可以避开上述限制
- 在根目录运行`python ./src/tencent-poi-aed-map.py`即可


