# 本包是爬取链家的 返回字典列表
import time
import requests     # 导入请求模块
from bs4 import BeautifulSoup  # 导入BeautifulSoup库
import re
import pandas as pd
from .models import CustomException


# 百度api根据address查坐标
# city 中文！
def get_coordinate(address, city_chn: str):
    # 将地址转换为经纬度
    addr_params = {'address': address, 'output': 'json', 'ak': '25QIApw6F3kfB4SWDcKDswwA4aCkBZjj', 'city': {city_chn}}
    addr_url = 'http://api.map.baidu.com/geocoding/v3/'
    addr_response = requests.get(addr_url, params=addr_params)
    addr_json = addr_response.json()
    location = addr_json['result']['location']
    lng = location['lng']
    lat = location['lat']
    #print(lng, ",", lat)
    return [lng, lat]


# 爬取链家租房信息 参数1.url为请求地址 2.page为当前页数 返回爬到的信息的列表
def lianjia_get(url: str, page: int, city: str, city_chn: str) -> list:
    # 防止被反爬触发 1秒访问一次
    time.sleep(1)
    # url = 'https://gz.lianjia.com/zufang/#contentList'     # 创建请求地址
    # 创建模拟浏览器的请求头信息
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    try:
        response = requests.get(url=url,headers=headers)   # 发送网络请求
    except Exception as e:
        raise CustomException("请求网站未响应，可能是城市名错误")
    response.encoding='utf-8'                          # 设置编码方式
    # 创建一个BeautifulSoup对象，获取页面正文
    soup = BeautifulSoup(response.text, features="lxml")
    # 使用正则表达式匹配租房信息
    html = soup.prettify()
    # 正则不匹配换行符？ 所以加re.DOTALL
    matches = re.findall('<div class="content__list--item--main">(.*?)</div>', html, re.DOTALL)
    # 图片链接
    matches2 = re.findall('<a class="content__list--item--aside".*?data-src="(.*?)"', html, re.DOTALL)

    # 保存爬到的数据
    datas = []
    # index要唯一 这个是0-30循环 得加上页数*30
    for index, match in enumerate(matches):
        # .*? 非贪婪匹配所有字符 遇到第一个结束
        # (.*?)就是提取你要的字符串 不加括号就是忽略你想忽略的
        # \s*匹配任意数量空白 包括换行符
        # [0]返回的是列表 只要第一个结果
        # \d{1, 10}匹配1到10个数字。
        # \.\d{1, 2}匹配一个点后跟1到2个数字，表示小数部分。
        # .{1,10} 匹配任意字符且长度为1到10个字符 贪婪 非贪婪：.{1,10}?
        # (\S{1,10}) 匹配非空格字符且长度为1到10个字符
        # price 两个()返回元组列表[(a,b)]
        loca = re.findall(r'<a href="/.*?/" target="_blank">\s*(.*?)\s*</a>', match, re.DOTALL)
        dis = re.findall(r'<a href="/.*?/" target="_blank" title=".*?">\s*(.*?)\s*</a>', match, re.DOTALL)
        size = re.findall(r'</i>\s*(\d{1,10})\..{0,10}㎡\s*<i>', match, re.DOTALL)
        price = re.findall(r'<span class="content__list--item-price">\s*<em>\s*(\d{1,10})\S{0,1}(\S*)\s*</em>', match, re.DOTALL)
        link = re.findall(r'<p class="content__list--item--title">\s*<a class="twoline" href="(.*?)"', match, re.DOTALL)
        # 如果价格有最高最低 取平均
        if price[0][1]:
            price = [int((int(price[0][0]) + int(price[0][1])) / 2)]
        else:
            price = [price[0][0]]
        # 前三个元素不为空 是一种html格式
        if dis:
            data = {"index": index + page*30, "地点": loca, "小区": dis, "面积": int(size[0]), "价格": int(price[0]),
                    "每平方租金": int(int(price[0])/int(size[0])), "访问链接": f"https://gz.lianjia.com{link[0]}",
                    "坐标": get_coordinate(loca+dis, city_chn)}
            data["图片"] = matches2[index]
            datas.append(data)
        else:
            dis = re.findall(r'<p class="content__list--item--title twoline">\s*<a href="(.*?)".*?>\s*(\S{1,25})\s(\S{1,25}).*?</a>', match, re.DOTALL)
            if not size:
                size = re.findall(r'<p class="content__list--item--des">\s*(\d{1,16})\..{0,16}㎡\s*<i>', match, re.DOTALL)
            if dis:
                data = {"index": index + page*30, "地点": loca, "小区": [dis[0][1],dis[0][2]], "面积": int(size[0]), "价格": int(price[0]),
                        "每平方租金": int(int(price[0])/int(size[0])), "访问链接": f"https://gz.lianjia.com{dis[0][0]}"
                        }
                data["坐标"] = get_coordinate(data["地点"] + data["小区"], city_chn)
            else:
                # 这一条纯粹防dis空
                data = {"index": index + page*30, "地点": loca, "小区": [dis], "面积": int(size[0]), "价格": int(price[0]),
                        "每平方租金": int(int(price[0]) / int(size[0])),
                        "访问链接": f"https://gz.lianjia.com{dis}",
                        "坐标": get_coordinate(loca+dis, city_chn)}
            data["图片"] = matches2[index]
            datas.append(data)

    # print(html)
    # print(datas)

    return datas


# 本地发出请求爬取 参数c为发起请求到的页数（次数）返
# 返回爬到的信息的列表
# callback为send_sth !!要await
async def local_scr(page: int, callback, city: str = "gz", city_chn: str = "广州") -> list:
    print("local_scr")
    datas = []
    if city == "":
        city = "gz"
    if city_chn == "":
        city_chn = "广州"
    err_count = 0
    i = 1
    while i <= page:
        print(f"爬取第{i}页中")
        await callback(f"爬取第{i}页中")
        try:
            datas += lianjia_get(f'https://{city}.lianjia.com/zufang/pg{i}/#contentList', i, city, city_chn)
            err_count = 0
        except Exception as e:
            if err_count == 3:
                print("连续错误三次，结束爬取")
                await callback("连续错误三次，结束爬取")
                break
            print("爬取错误：", e, "5秒后将重新尝试一次")
            await callback("爬取错误：", e, "5秒后将重新尝试一次")
            i -= 1
            err_count += 1
            time.sleep(5)
        finally:
            i += 1
    return datas


if __name__ == '__main__':
    datas = local_scr(1, print)
    # print(datas)
# 将数据转换为 pandas DataFrame
# df = pd.DataFrame(datas)

# 将 DataFrame 导出到 Excel 文件
# df.to_excel('output2.xlsx')




