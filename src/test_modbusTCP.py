import time
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

# Kết nối PLC
client = ModbusTcpClient('10.16.40.160', port=502)

def read_real_from_offset(offset_byte):
    address = offset_byte // 2
    result = client.read_holding_registers(address, 2, unit=1)
    if not result.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        return decoder.decode_32bit_float()
    else:
        print(f"❌ Lỗi đọc tại offset {offset_byte}")
        return None

variables = {
    "DifferentialTotalFlow": 0,
    "ReverseTotalFlow": 4,
    "ForwardFlow": 8,
    "Flow": 16,
    "FlowRate": 20,
}

if client.connect():
    print("✅ Kết nối thành công đến PLC. Đang đọc dữ liệu... (Ctrl + C để thoát)\n")
    try:
        while True:
            print(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            for name, offset in variables.items():
                value = read_real_from_offset(offset)
                display_value = round(value, 1) if value is not None else "-"
                print(f"{name:25}: {display_value}")
            print("-" * 40)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng đọc.")
    finally:
        client.close()
else:
    print("❌ Không thể kết nối đến PLC.")
