import math
import numpy as np
import pyaudio

from midi import notes
from read_midi import auto_run

# 输入的mid
cry_mid = auto_run()
# 参数设置
sample_rate = 44100
bpm = 97
beat_duration = 60 / bpm
time_step_duration = beat_duration / 4
rate = 2 ** (0 / 12)
blankt = 441  # 每个音前停顿帧数 其时间为blankt/sample_rate

blankarr = np.zeros(blankt)  # 平滑上升
for i in range(int(blankt/4)):
    blankarr[-i-1]=(np.cos(np.pi/int(blankt/4)*i)+1)/2


# 初始化 PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)

# 初始化音轨状态
# 每个标签记录是否启用 频率（音高） 相位
track_states = [{"active": False, "freq": None, "phase": 0.0} for _ in range(4)]

# 播放 MIDI 序列（修改波形生成部分）
for step_idx, step in enumerate(cry_mid):
    print(f"{math.floor(step_idx / 12) + 1}: {math.floor((step_idx % 12) / 4) + 1}-{step_idx % 4 + 1}{step} {step_idx}")
    composite_signal = np.zeros(int(sample_rate * time_step_duration), dtype=np.float32)

    for track_idx in range(4):
        note = step[track_idx]
        current_state = track_states[track_idx]

        # 解析音符指令
        if note == "00":
            current_state["active"] = False
            current_state["freq"] = None
            current_state["phase"] = 0.0
        elif note == "--":
            pass  # 延续状态
        elif note in notes:
            current_state["active"] = True
            current_state["freq"] = notes[note] * rate
            current_state["phase"] = 0.0

        # 生成波形
        if current_state["active"] and current_state["freq"] is not None:
            # 生成时间轴（考虑相位连续性）
            t = np.linspace(
                current_state["phase"],
                current_state["phase"] + time_step_duration,
                int(sample_rate * time_step_duration),
                endpoint=False
            )


            if track_idx < 4:
                # 方波生成逻辑：根据相位生成
                square_wave = np.where(
                    np.sin(2 * np.pi * current_state["freq"] * t) > 0, 0.1, 0)  # 判断正弦波相位 正半周/负半周
                if not note in ("00", "--"):
                    square_wave[:blankt] *= blankarr[:blankt]
            else:
                square_wave = np.sin(2 * np.pi * current_state["freq"] * t) * 0.26  # 正弦波

            composite_signal += square_wave  # 叠加到复合信号
            current_state["phase"] += time_step_duration  # 更新相位（保持连续性）
            current_state["phase"] %= 1 / current_state["freq"]  # 相位保持在周期内

    stream.write(composite_signal.astype(np.float32).tobytes())  # 播放音频

# 清理资源
stream.stop_stream()
stream.close()
p.terminate()
