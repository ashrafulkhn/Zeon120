
def binaryToDecimal(binary):
    decimal, i = 0, 0
    while (binary != 0):
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary//10
        i += 1
    return decimal


def bytetobinary(x):
    b = []
    for my_byte in x:
        b.append(f'{my_byte:0>8b}')
    return b


class DTH:
    @staticmethod
    def convertohex(val):
        arr = []
        tmp = int(val * 1000)
        hexval = hex(tmp)[2:].zfill(6)
        val1 = int(hexval[:2], 16)
        arr.append(val1)
        val2 = int(hexval[2:4], 16)
        arr.append(val2)
        val3 = int(hexval[4:6], 16)
        arr.append(val3)
        return arr

    @staticmethod
    def converttohexforpecc(val):
        arr1 = []
        hexval = val[2:].zfill(4)
        val1 = int(hexval[:2], 16)
        arr1.append(val1)
        val2 = int(hexval[2:4], 16)
        arr1.append(val2)
        return arr1


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
