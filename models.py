# 自定义异常模块
class CustomException(Exception):
    def __init__(self, message: str):
        self.message = message