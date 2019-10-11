class Account:
    def __init__(self, name, password, accType, accNum=0, sequence=0, address='',
                 pubkey=''):
        self.__name = name
        self.__password = password
        self.__accNum = accNum
        self.__sequence = sequence
        self.__address = address
        self.__accType = accType
        self.__pubkey = pubkey
        self.__coinDict = {}

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def setPassword(self, password):
        self.__password = password

    def getPassword(self):
        return self.__password

    def setAccNum(self, accNum):
        self.__accNum = accNum

    def getAccNum(self):
        return self.__accNum

    def setSequence(self, sequence):
        self.__sequence = sequence

    def getSequence(self):
        return self.__sequence

    def setAddress(self, address):
        self.__address = address

    def getAddress(self):
        return self.__address

    def setAccType(self, accType):
        self.__accType = accType

    def getAccType(self):
        return self.__accType

    def setPubkey(self, pubkey):
        self.__pubkey = pubkey

    def getPubkey(self):
        return self.__pubkey

    def __str__(self):
        return self.__dict__

    def setCoins(self, coins):
        for coin in coins:
            self.__coinDict[coin['denom']] = coin['amount']

    def getCoins(self):
        return self.__coinDict
