import serial
import time

def send_receive(serial_port, command):
    serial_port.write(command)
    time.sleep(5)
    response = serial_port.read(serial_port.inWaiting())
    return response

def generate_command(transaction_type):
    SOH = b'\x01'
    transaction = transaction_type.encode()
    DATA = transaction.ljust(996, b' ') 
    LEN = len(DATA).to_bytes(2, 'little')
    LRC = (LEN[0] ^ LEN[1])
    for b in DATA:
        LRC ^= b
    LRC = LRC.to_bytes(1, 'big')
    command = SOH + LEN + DATA + LRC
    return command

def check_card_machine_version(port):
    with serial.Serial(port, 9600, timeout=1) as serial_port:
        command = generate_command("99")
        response = send_receive(serial_port, command)
        if response[:2] == b'\x06\x06':
            return response[2:].decode()
        else:
            return "未收到有效回應"
version_info = check_card_machine_version('COM10')
print(version_info)
