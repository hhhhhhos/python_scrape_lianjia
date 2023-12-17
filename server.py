# region socket库服务器（不支持websocket客户端）
""" tcp socket 不支持vue的websocket
# -*- coding:utf-8 -*-
import socket
import subprocess # 执行linux命令的
import threading
import time

host = '0.0.0.0'  # 主机IP
port = 8080  # 端口号
web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
web.bind((host, port))  # 绑定端口
web.listen(1)  # 设置最多连接数
print('服务器等待客户端连接...')

# 查看套接字状态
def get_sock_stats(sock_stats_return):
    # 创建一个管道，运行ss命令并结合grep过滤本地端口号为8080的连接
    process = subprocess.Popen(f'netstat -tun | grep 0.0.0.0:{port}', shell=True, stdout=subprocess.PIPE)

    # 获取命令的输出
    output, error = process.communicate()
    new_return = output.decode()

    # 如果有变化 打印命令的输出
    if sock_stats_return == new_return:
        pass
    else:
        print("tcp:", new_return)
    return new_return

def thread_1():
    sock_stats_return = ""
    while True:
        time.sleep(0.2)
        sock_stats_return = get_sock_stats(sock_stats_return)


thread = threading.Thread(target=thread_1)
thread.start()
while True:
    print("阻塞等待中")
    conn, addr = web.accept()  # 建立客户端连接
    print("接收到连接成功，地址：" + str(addr))
    try:
        while True:
            # 接收客户端发送的数据 阻塞
            data = conn.recv(1024)  # 接收数据的最大字节数
            print("客户端发送的数据：" + data.decode())  # 打印数据

            response = input("请输入要发送的数据：")  # 提示用户输入数据
            conn.sendall(response.encode())
    except Exception as e:
        print(f"连接{str(addr)}发生异常：{e}")

    print(f"关闭{str(addr)}的链接")
    conn.close()  # 关闭链接

"""
# endregion
# region 引用
import json
import re
import subprocess
import threading
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
import asyncio
from . import demo
from .models import CustomException
# endregion

app = FastAPI()

# region 全局变量(上线不用)
sock_stats_return = ""
player = []
# endregion



# region 监控状态的线程模块
# 查看套接字状态
def get_sock_stats(sock_stats_return):
    # 创建一个管道，运行ss命令并结合grep过滤本地端口号为8080的连接
    process = subprocess.Popen(f'netstat -ano | findstr :8002', shell=True, stdout=subprocess.PIPE)

    # 获取命令的输出
    output, error = process.communicate()
    new_return = output.decode()

    # 如果有变化 打印命令的输出
    if sock_stats_return == new_return:
        pass
    else:
        if new_return != "":
            print("tcp:", new_return)
        else:
            print("tcp: (为空，已经关闭)")
    return new_return

def sock2():
    old_player = ['nothing']
    global player
    global sock_stats_return
    while True:
        if old_player != player:
            print("当前player:", player)
            old_player = player.copy() # 这里小心 直接等号将是址传递 而不是值传递
        sock_stats_return = get_sock_stats(sock_stats_return)
        time.sleep(0.2)


sock_thread = threading.Thread(target=sock2)
sock_thread.start()
# endregion

# region 套接字 爬虫大作业功能模块
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    # region 功能函数

    # 发起爬虫函数
    # callback回调函数为websocket.send_text(json.dumps(x))
    # callback参数必须为字典
    # callback要await
    async def do_sth(params: dict, callback, sendsth_callback):
        print("dosth")
        if params.get('page'):
            print("dosth2")
            if 1 <= int(params['page']) <= 3:
                print("dosth3")
                datas = await demo.local_scr(int(params.get('page')), sendsth_callback, params.get('city'), params.get('city_chn'))
                if datas:
                    await sendsth_callback("爬取成功，返回数据")
                    await callback({
                        "method": "data",
                        "params": {
                            "message": datas
                        }
                    })
            else:
                print("raise CustomException")
                raise CustomException("页数不正确")
        else:
            print("raise CustomException")
            raise CustomException("dosth params error")

    # 发送信息到客户端函数
    async def send_sth(msg: str):
        await websocket.send_text(json.dumps({
            "method": "console",
            "params": {
                "message": msg
            }
        }))

    # endregion

    # region 引入全局变量/定义局部变量
    global player
    client_ip = None
    client_port = None
    # endregion

    # region websocket try处理
    try:
        await websocket.accept()

        # region 只允许一个连接者的判断
        if player:
            # 创建一个管道，运行ss命令并结合grep过滤本地端口号为8080的连接 WIN命令
            process = subprocess.Popen(f'netstat -ano | findstr {player[0]}', shell=True, stdout=subprocess.PIPE)
            # 获取命令的输出
            output, error = process.communicate()
            new_return = output.decode()
            new_return = re.findall(r'\s+\S+\s+\S+\s+\S+\s+(\S+)\s+', new_return, re.DOTALL)
            print(new_return)
            await send_sth(f"已有连接者：{player[0]}，状态：{new_return[0]}")
            await send_sth(f"为防止反爬/被封ip，请等待{player[0]}退出后重试")
            raise CustomException("已有链接")
        # endregion

        # region 获取ip,端口/返回客户端ip,端口/全局player加入ip,端口
        client_ip = websocket.client.host
        client_port = websocket.client.port
        print(f"连接者: {client_ip}:{client_port}")
        await send_sth(f"{client_ip}:{client_port}已连接")
        player.append(f"{client_ip}:{client_port}")
        # endregion


        # region 等待接收信息 5秒超时/json转dict
        # 这里收到的是字符串
        # 5秒收不到新信息断开
        data = await asyncio.wait_for(websocket.receive_text(), timeout=5)
        print("收到：", data)
        # 将类似json的字符串转换为python字典
        data = json.loads(data)
        # endregion

        # region 收到信息 做点什么... 防空判断
        if data.get('method') and data['method'] == "爬虫":
            # 兰博表达式
            if data.get('params'):
                await do_sth(data['params'], lambda x: websocket.send_text(json.dumps(x)), send_sth)
            else:
                raise CustomException("params不存在")
            #await send_sth("hello")
        else:
            raise CustomException("method不存在")

        # 字典转json格式字符串
        # data = json.dumps(data)
        # await websocket.send_text(data)
        # endregion

    # endregion

    # region 异常处理
    # 对方断开连接
    except WebSocketDisconnect:
        print(f"{client_ip}:{client_port}断开了连接")
        print("客户端断开链接，发起return")
        # 这里必须return 不然下面最后会在已关闭的socket上发送信息 gg
        return
        # player -= 1
    # 等待对方发送超时
    except asyncio.TimeoutError as e:
        print(f"Timeout!：{str(e)}")
        await send_sth("等待接收信息超时，自动断开")
    # 自定义异常
    except CustomException as e:
        print(f"自定异常：{e.message}")
        await send_sth(f"发生异常：{str(e)}")
    # player超过1或其他异常
    except Exception as e:
        print(f"发生了一个异常：{str(e)}")
        await send_sth(f"发生异常：{str(e)}")
    # endregion

    # region 结束链接 结尾处理
    player.remove(f"{client_ip}:{client_port}")
    print("正常结束")
    await send_sth(f"{client_ip}:{client_port}正常结束，断开")
    await websocket.close()
    # endregion

# endregion
