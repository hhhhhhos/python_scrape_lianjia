# 本包主要是输入地址返回百度地图坐标
import urllib.parse
import requests
import webbrowser

# 百度api根据address查坐标
def get_coordinate(address):
    # 将地址转换为经纬度
    addr_params = {'address': address, 'output': 'json', 'ak': '25QIApw6F3kfB4SWDcKDswwA4aCkBZjj', 'city': '广州市'}
    addr_url = 'http://api.map.baidu.com/geocoding/v3/'
    addr_response = requests.get(addr_url, params=addr_params)
    addr_json = addr_response.json()
    location = addr_json['result']['location']
    lng = location['lng']
    lat = location['lat']
    #print(lng, ",", lat)
    return [lng, lat]

# 我不用的功能
def get_static_map(address):
    # 将地址转换为经纬度
    addr_params = {'address': address, 'output': 'json', 'ak': '25QIApw6F3kfB4SWDcKDswwA4aCkBZjj', 'city': '广州市'}
    addr_url = 'http://api.map.baidu.com/geocoding/v3/'
    addr_response = requests.get(addr_url, params=addr_params)
    addr_json = addr_response.json()
    location = addr_json['result']['location']
    lng = location['lng']
    lat = location['lat']
    print(lng, ",", lat)

    # 获取静态地图
    static_url = 'http://api.map.baidu.com/staticimage/v2'
    static_params = {'center': f'{lng},{lat}', 'width': '500', 'height': '300', 'zoom': '15', 'markers': f'{lng},{lat}', 'ak': '25QIApw6F3kfB4SWDcKDswwA4aCkBZjj'}
    static_response = requests.get(static_url, params=static_params)
    static_image = static_response.content

    # 保存地图图片
    with open('static_map.png', 'wb') as f:
        f.write(static_image)

    # 在浏览器中打开地图图片
    webbrowser.open('static_map.png')



# 使用百度地图的逆地理编码API将经纬度转换为地址信息。# 我没权限
def reverse_geocode(lat, lng, ak='25QIApw6F3kfB4SWDcKDswwA4aCkBZjj'):
    """
    使用百度地图的逆地理编码API将经纬度转换为地址信息。

    参数:
    lat -- 纬度值
    lng -- 经度值
    ak -- 您的百度地图API密钥
    """
    # 构建请求URL
    url = 'http://api.map.baidu.com/geocoder/v2/'
    params = {
        'ak': ak,
        'callback': 'renderReverse',
        'location': f'{lat},{lng}',
        'output': 'json',
        'pois': 0
    }

    # 发送GET请求
    response = requests.get(url, params=params)
    return response



# 使用示例



if __name__ == '__main__':
    #print(reverse_geocode(39.983424, 116.322987).json())
    address = input('请输入地址：')
    #get_static_map(address)
    print(get_coordinate(address))
