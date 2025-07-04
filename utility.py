
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

class DigitalOutputFrameBuilder:
    @staticmethod
    def build_contact_status_frame(digital_out_data: list[int]) -> list[int]:
        """
        Build the CAN data frame to set the digital output statuses.
        
        Parameters:
            digital_out_data (list of int): A list of 0s and 1s, length 15, each representing the state of D1 to D15.
        
        Returns:
            list[int]: A 4-byte CAN data frame.
        """
        if len(digital_out_data) < 15:
            raise ValueError("digital_out_data must be at least 15 elements long (D1 to D15).")

        # Extract D1–D8 and D9–D15
        d1_to_d8 = digital_out_data[0:8]
        d9_to_d15 = digital_out_data[8:15]

        # Convert to binary numbers
        data_byte_1 = sum((bit << i) for i, bit in enumerate(d1_to_d8))
        data_byte_2 = sum((bit << i) for i, bit in enumerate(d9_to_d15))

        # Create the masks: mask = 1 where we want to apply changes
        mask_byte_1 = 0xFF  # Enable all for D1–D8
        mask_byte_2 = 0x7F  # Only 7 bits used for D9–D15
        
        
        return [data_byte_1, data_byte_2, mask_byte_1, mask_byte_2]

# Usage example
if __name__ == "__main__":
    digital_out_data = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1]  # 15 values
    frame_data = DigitalOutputFrameBuilder.build_contact_status_frame(digital_out_data)
    print("Message sent:", frame_data)
