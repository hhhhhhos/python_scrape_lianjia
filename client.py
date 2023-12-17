import socket       # 导入socket模块
import threading
import time
import subprocess # 执行linux命令的

host = '43.139.15.96'  # 获取主机地址
port = 8080        # 设置端口号
#s.connect((host,port)) # 主动初始化TCP服务器连接

# 向服务端进行socket通信 s为套接字对象
def sock(s):
    try:
        # s.close()之后 再次s.connect((host, port))就失效了
        #s = socket.socket()  # 创建TCP/IP套接字
        s.connect((host, port))  # 主动初始化TCP服务器连接
        print("链接成功")

        while True:
            # 向服务器发送信息
            send_data = input("请输入要发送的数据：") # 提示用户输入数据
            s.send(send_data.encode()) # 发送TCP数据


            # 接收服务器发送过来的数据，最大接收1024个字节
            print("已发送，等待回信中...")
            recvData = s.recv(1024).decode()
            print('接收到的数据为:',recvData)

            # 关闭套接字
            #s.close()
    except Exception as e:
        print("连接或接收失败：" + str(e))
        print("5秒后重试")
        time.sleep(5)

# 查看套接字状态
def get_sock_stats(sock_stats_return):
    # 创建一个管道，运行ss命令并结合grep过滤本地端口号为8080的连接
    process = subprocess.Popen(f'netstat -ano | findstr 43.139.15.96:{port}', shell=True, stdout=subprocess.PIPE)

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

# study
def sock2():
    s = socket.socket()
    s.connect((host, port))  # 主动初始化TCP服务器连接
    while True:
        send_data = input("请输入要发送的数据：")  # 提示用户输入数据
        if send_data == "exit":
            break
        s.send(send_data.encode())  # 发送TCP数据

        # 接收服务器发送过来的数据，最大接收1024个字节
        print("已发送，等待回信中...")
        recvData = s.recv(1024).decode()
        if recvData == "":
            print("服务端终止了套接字")
            break
        print('接收到的数据为:', recvData)

    print("客户端close")
    s.close()

# 测试socket
sock_thread = threading.Thread(target=sock2)
sock_thread.start()

sock_stats_return = ""
while True:
    sock_stats_return = get_sock_stats(sock_stats_return)
    time.sleep(0.2)

count = 0
while False:
    print(f"第{count}次socket")
    s = socket.socket()  # 创建TCP/IP套接字
    sock_thread = threading.Thread(target=sock, args=(s,))
    sock_thread.start()
    sock_stats_return = ""
    while sock_thread.is_alive():
        sock_stats_return = get_sock_stats(sock_stats_return)
        time.sleep(0.2)
    count += 1