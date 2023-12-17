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
import subprocess
import threading
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
import asyncio
app = FastAPI()

# 全局变量
sock_stats_return = ""
player = []

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


# 监控状态的线程
sock_thread = threading.Thread(target=sock2)
sock_thread.start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    global player
    if player >= 1:
        print("已经有一个玩家在连接中")
        raise HTTPException(status_code=400, detail="已经有一个玩家在连接中")
    player += 1
    """
    global player
    client_ip = None
    client_port = None
    try:
        await websocket.accept()
        client_ip = websocket.client.host
        client_port = websocket.client.port
        print(f"连接者: {client_ip}:{client_port}")
        player.append(f"{client_ip}:{client_port}")


        send = 0
        while True:
            data = await websocket.receive_text()
            print("收到：",data)
            send += 1
            await websocket.send_text(str(send))

    except WebSocketDisconnect:
        print(f"{client_ip}:{client_port}断开了连接")
        player.remove(f"{client_ip}:{client_port}")
        # await websocket.close()
        # player -= 1
    except Exception as e:
        print(f"发生了一个异常：{e}")
