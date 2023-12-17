import subprocess

# 创建一个管道，运行ss命令并结合grep过滤本地端口号为8080的连接
process = subprocess.Popen('ss -o state all | grep :8080', shell=True, stdout=subprocess.PIPE)

# 获取命令的输出
output, error = process.communicate()

# 打印命令的输出
print("tcp:", output.decode())
#print(output.decode()[7:18])