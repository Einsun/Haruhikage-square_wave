def read_file_as_hex(file_path, lines=-1, bytes_per_line=16):
    """
    读取文件并以 Hex 格式显示内容
    :param file_path: 文件路径
    :param lines: 显示行数（默认-1为全显示）
    :param bytes_per_line: 每行显示的字节数（默认 16,1字节为2个16进制数）
    """
    try:
        with open(file_path, 'rb') as file:  # 以二进制模式打开文件
            offset = 0  # 文件偏移量
            while lines != 0:
                chunk = file.read(bytes_per_line)  # 读取指定字节数
                if not chunk:  # 如果读取完毕，退出循环
                    break
                print_trunk(offset, chunk, bytes_per_line)
                offset += bytes_per_line  # 更新偏移量

                lines -= 1

    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
    return 0


def print_trunk(offset, chunk, bytes_per_line):
    # 将字节转换为 Hex 字符串
    hex_values = ' '.join(f'{byte:02X}' for byte in chunk)

    # 将字节转换为可打印字符（非可打印字符显示为 '.'）
    printable = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)

    # 打印偏移量、Hex 值和可打印字符
    print(f'{offset:08X}  {hex_values:<{bytes_per_line * 3}}  {printable}')


# 快速二进制打印
def print_tiny(chunk):
    """
    :param chunk: 16进制原始数据
    :return: 无
    """
    # 将字节转换为 Hex 字符串
    hex_values = ' '.join(f'{byte:02X}' for byte in chunk)
    print(f'{hex_values}')


# 将音调数值对应音符
def midi_to_note_name(midi_number):
    """
    将 MIDI 音符编号转换为音调文本
    :param midi_number: MIDI 音符编号（0-127）
    :return: 音调文本（如 "C4"）
    """
    # 音符名称列表
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # 计算音符名称和八度
    if 0 <= midi_number <= 127:
        note_index = midi_number % 12  # 音符名称索引
        octave = midi_number // 12 - 1  # 八度
        return f"{note_names[note_index]}{octave}"
    else:
        raise ValueError("MIDI 音符编号必须在 0 到 127 之间")


def midi_read(file_path):
    # """
    # 读取midi原始文件
    # :param file_path:将要读取文件的路径
    # :return: array,base_data
    #     arrays[]: 解析后的MIDI数据数组。
    #     base_data[0]:midi文件路径
    #     base_data[1]:全局常量[]
    #         全局常量[0]:midi类型（0:单轨道类型;1:多轨道标准类型;2:非标准多轨道）
    #         全局常量[1]:轨道数量
    #     全局常量[2]:时间数据精度
    #     base_data[2:]:音轨元数据[]
    # """
    """
    读取MIDI原始文件并解析其内容。

    Args:
        file_path (str): MIDI文件的路径。

    Returns:
        tuple: 包含两个元素的元组 (arrays, base_data)。
            - arrays: 解析后的MIDI数据数组。
            - base_data: 包含MIDI文件的基本信息和元数据的列表，具体结构如下：
                - base_data[0] (str): MIDI文件的路径。
                - base_data[1] (list): 全局常量列表，包含以下内容：
                    - 全局常量[0] (int): MIDI类型：
                        - 0: 单轨道类型
                        - 1: 多轨道标准类型
                        - 2: 非标准多轨道类型
                    - 全局常量[1] (int): 轨道数量。
                    - 全局常量[2] (int): 时间数据精度。
                - base_data[2:] (list): 音轨元数据列表，每个元素代表一个音轨的元数据。
    """
    arrays = []
    base_data = [file_path]
    with open(file_path, 'rb') as file:  # 以二进制模式打开文件

        chunk = file.read(8)  # 读取指定字节数
        # hex_values = ' '.join(f'{byte:02X}' for byte in chunk)
        # print(hex_values)
        # print("以上为文件头")
        # for b in chunk:
        #     print(hex(b))

        chunk = file.read(6)  # 读取指定字节数
        hex_values = ' '.join(f'{byte:02X}' for byte in chunk)
        # print(hex_values)
        base_data.append([chunk[0] << 8 | chunk[1], chunk[2] << 8 | chunk[3], chunk[4] << 8 | chunk[5]])
        print("模式:", base_data[1][0], hex(base_data[1][0]))
        print("轨道数:", base_data[1][1], hex(base_data[1][1]))
        print("时间分度:", base_data[1][2], hex(base_data[1][2]))

        print("===============================================")

        for i in range(3):

            chunk = file.read(8)  # 读取指定字节数
            # hex_values = ' '.join(f'{byte:02X}' for byte in chunk)
            # print(hex_values)
            # print("标志头", chunk[0:4])
            if chunk[:4] == b'MTrk':
                date_len = chunk[4] << 8 * 3 | chunk[5] << 8 * 2 | chunk[6] << 8 * 1 | chunk[7]
                # print("数据量[", i, "]:", date_len)
            else:
                break

            # print("-------")

            chunk = file.read(date_len)  # 读取指定字节数

            hex_values = ' '.join(f'{byte:02X}' for byte in chunk)
            # print(hex_values)
            # for b in chunk:
            # print(b)
            if chunk[-4:] != b'\x00\xff/\x00':
                break
            # else:
            #     print("标志尾", chunk[-4:])

            flag = 0
            delta_time = 0
            add_time = 0
            model = 0
            array = []
            while flag + 4 < date_len:
                delta_time = 0
                while chunk[flag] > 0x80:
                    delta_time = delta_time << 7 | chunk[flag] - 0x80
                    flag += 1
                delta_time = delta_time << 7 | chunk[flag]

                delta_time = int(delta_time / base_data[1][2] * 4)
                add_time += delta_time  # 时间偏移量
                flag += 1

                if chunk[flag] > 0x7f:
                    model = chunk[flag]
                    flag += 1

                if model < 0x7f:
                    continue

                elif model <= 0x8f:
                    if __name__ == "__main__":
                        print(" 时间变化量:", delta_time,
                              " 时间偏移量:", add_time,
                              " 释放标记", hex(model),
                              " 音符音调", chunk[flag],
                              " 音符强度", chunk[flag + 1])
                    flag += 2
                    array.append([add_time, delta_time, 0, chunk[flag - 2]])



                elif model <= 0x9f:
                    if __name__ == "__main__":
                        print(" 时间变化量:", delta_time,
                              " 时间偏移量:", add_time,
                              " 按下标记", hex(model),
                              " 音符音调", chunk[flag],
                              " 音符强度", chunk[flag + 1])
                    flag += 2
                    array.append([add_time, delta_time, 1, chunk[flag - 2]])

                # 乐器设置
                elif model <= 0xcf:
                    if __name__ == "__main__":
                        print(" 时间变化量:", delta_time,
                              " 时间偏移量:", add_time,
                              " 设置标记:", hex(model),
                              " 乐器类型:", hex(chunk[flag]))
                    flag += 1

                # 元数据设置
                elif model == 0xff:
                    dlen = chunk[flag + 1]  # 接下来的数据长度
                    data = chunk[flag + 2:flag + 2 + dlen]  # 接下来的数据
                    tempo = 0
                    for t_dat in data:
                        tempo = tempo << 8 | t_dat
                    bpm = 60000000 / tempo
                    if __name__ == "__main__":
                        print(" 元事件标志:", hex(chunk[flag - 1]),
                              " 元事件类型:", hex(chunk[flag]),
                              " 以下数据长度:", dlen, hex(chunk[flag + 1]),
                              " BPM设置:", bpm, hex(tempo))
                    base_data.append([flag,chunk[flag],bpm])
                    flag += dlen + 2

            # print(array)
            arrays.append(array)
            if __name__ == "__main__":
                print("===============================================")
    return arrays, base_data


# 根据midi格式的列表 转为mod格式的列表
def midi_change(arrays):
    """
    :param arrays: 解析后的MIDI数据数组
    :return: 转换后的MIDI数据数组
    """
    array2 = arrays[1]
    array1 = arrays[2]
    array_midi = []

    for i in range(max(array1[-1][0], array2[-1][0]) + 1):
        array_midi.append(["00", "00", "00", "00"])

    num = 0
    mid = ["00", "00", "00", "00"]
    for j in array1:
        if j[1]:  # 如果有时间经过
            for _ in range(j[1]):
                for i in range(4):
                    if mid[i] != "00":
                        array_midi[num + 1][i] = "--"
                num += 1

        if j[2]:  # 如果是按下
            for i in range(4):
                if array_midi[num][i] == "00":
                    array_midi[num][i] = midi_to_note_name(j[3])
                    mid[i] = midi_to_note_name(j[3])
                    break

        else:  # 如果是释放
            for i in range(4):
                if mid[i] == midi_to_note_name(j[3]):
                    mid[i] = "00"
                    array_midi[num][i] = "00"
                    break

        if num != j[0]:
            print(num, j)
            print("err")
            break

    num = 0
    mid = ['00', '00', '00', '00']
    for j in array2:

        if j[1]:  # 如果有时间经过
            for _ in range(j[1]):
                for i in range(3, 0, -1):
                    if mid[i] != "00":
                        array_midi[num + 1][i] = "--"
                num += 1

        if j[2]:
            for i in range(3, 0, -1):
                if array_midi[num][i] == "00":
                    array_midi[num][i] = midi_to_note_name(j[3])
                    mid[i] = midi_to_note_name(j[3])
                    break
        else:
            for i in range(3, 0, -1):
                if mid[i] == midi_to_note_name(j[3]):
                    mid[i] = "00"
                    array_midi[num][i] = "00"
                    break

        if num != j[0]:
            print(num, j)
            print("err")
            break

    return array_midi


# 自动读取文件 返回列表
def auto_run():
    file_path = "Haruhikage.mid"  # 文件路径
    arrays,base_data = midi_read(file_path)
    array_midi = midi_change(arrays)
    print(base_data)
    return array_midi


if __name__ == "__main__":
    read_file_as_hex("Haruhikage.mid", 32)
    midi = auto_run()
    for a in range(len(midi)):
        print(f"{a} {midi[a]}")
