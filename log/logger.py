class Logger:
    def __init__(self, time):
        self.__time = time

    def Warn(self, msg):
        self.__type = '<Warn> '
        self.__msg = msg
        return self.__time + '<Warn> ' + msg

    def Info(self, msg):
        self.__type = '<Info> '
        self.__msg = msg
        return self.__time + '<Info> ' + msg

    def Error(self, msg):
        self.__type = '<Error> '
        self.__msg = msg
        return self.__time + '<Error> ' + msg

    def __str__(self):
        return self.__time + self.__type + self.__msg
