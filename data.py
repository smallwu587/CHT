import serial
import time
import pushdata as pd

path = 'output.txt'


f = open (path , 'a')
print("\n" , file=f)
def calculate_lrc(data):
    """ 計算 LRC 檢查碼。 """
    lrc = 0
    for byte in data:
        lrc ^= byte
    return lrc

def build_packet(data_positions, packet_length=1000):
    """ 根據指定的數據和位置建立並填充數據包。 """
    # 創建空數據包
    data_packet = [' ' for _ in range(packet_length)]

    # 遍歷所有數據，並將它們放在指定位置
    for data, position in data_positions.items():
        for i in range(len(data)):
            data_packet[position + i] = data[i]

    # 將數據包列表轉換為字符串
    data_str = ''.join(data_packet)

    # 編碼並計算 LRC，添加到數據包
    data_encoded = data_str.encode('utf-8')
    len_bytes = len(data_encoded).to_bytes(2, byteorder='little')
    packet = b'\x01' + len_bytes + data_encoded
    lrc = calculate_lrc(packet[1:])
    packet += bytes([lrc])

    return packet

def send_data(ser, packet):
    """ 發送資料到串列埠。 """
    ser.write(packet)
    print(f"已發送: {packet}"  , file=f)

def receive_response(ser):
    """ 接收並打印終端機的回應。 """
    try:
        ser.timeout = 10  # 設定 10 秒的等待回應時間
        response = ser.read(1000)  # 預期回應長度為 1000 字節
        if response:
            print(f"收到回應: {response.decode('utf-8', errors='ignore')}"  , file=f)
        else:
            print("未收到有效回應" , file=f)
    except Exception as e:
        print(f"接收回應時發生錯誤: {e}" , file=f)

def test_payment_terminal():
    """ 測試支付終端機通訊。 """
    try:
        ser = serial.Serial('COM10', 9600, bytesize=8, parity='N', stopbits=1, timeout=3)
        print("串列埠成功打開。" , file=f)
    except Exception as e:
        print(f"打開串列埠時發生錯誤: {e}" , file=f)
        return

    data_positions = pd.now

    packet = build_packet(data_positions)

    for attempt in range(1):
        send_data(ser, packet)
        if receive_response(ser):  # 現在會打印出任何回應
            break

    ser.close()
    print("串列埠已關閉。" , file=f)

test_payment_terminal()

f.close()