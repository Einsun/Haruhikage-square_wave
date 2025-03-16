from machine import Pin, PWM
from midi import cry_mid, notes, tick
import time
import math

# pwm输出
pwm1 = PWM(Pin(2))
pwm2 = PWM(Pin(4))
pwm3 = PWM(Pin(6))
pwm4 = PWM(Pin(8))
pwms = [pwm1, pwm2, pwm3, pwm4]

# pin输出
led = Pin(25, Pin.OUT)
pin1 = Pin(3, Pin.OUT)
pin2 = Pin(5, Pin.OUT)
pin3 = Pin(7, Pin.OUT)
pin4 = Pin(9, Pin.OUT)
pins = [pin1, pin2, pin3, pin4]

for i in range(4):
    pwms[i].duty_u16(0)  # 设置占空比为 0
    pwms[i].init()  # 初始化pwm
    pins[i].value(0)  # 设置相邻引脚为低电平


# 播放音符
def play_note(note):
    for i in range(4):
        if note[i] in notes:  # 如果是音符，则暂停上一个pwm
            pwms[i].duty_u16(0)  # 设置占空比为 0

    time.sleep(0.01)  # 暂停10ms表示音符停顿

    for i in range(4):
        if note[i] in notes:  # 如果是音符，则设置当前pwm频率
            frequency = notes[note[i]]  # notes[]中记录着对应评率
            pwms[i].freq(int(frequency))  # 设置当前pwm频率
            pwms[i].duty_u16(32768)  # 恢复占空比为 50%
        elif note[i] == "00":  # 如果是休止符，则设置当前pwm占空比
            pwms[i].duty_u16(0)  # 设置占空比为 0


while 1:
    msg = input("input")
    print(msg)
    if msg == "0":
        # for sound_note in mid:
        for i in range(0 * 12, len(cry_mid), 1):
            sound_note = cry_mid[i]
            print(f"{math.floor(i / 12) + 1}: {math.floor((i % 12) / 4) + 1}-{i % 4 + 1}{sound_note}")
            play_note(sound_note)
            time.sleep(tick - 0.01)
            if i % 12 < 4:
                led.value(1)
            else:
                led.value(0)

        for i in range(4):  # 最后关闭声音
            pwms[i].duty_u16(0)  # 设置占空比为 0
            pwms[i].deinit()  # 释放pwm

    elif msg == "1":
        for sound_note in cry_mid:
            print(sound_note)
            time.sleep(tick)

