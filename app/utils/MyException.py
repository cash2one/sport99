#coding=utf-8
#_author_ = jiangzhuang

class SQLException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ControllerException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
