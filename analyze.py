import math
import sys
import librosa
import json
import os
import numpy as np

def midi_to_note_name(midi_number):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = note_names[midi_number % 12]
    return f"{note}{octave}"

# # Đọc đường dẫn file từ tham số dòng lệnh
# file_path = sys.argv[1]  

def analyze_pitch(file_path):
    # Tải file âm thanh
    y, sr = librosa.load(file_path)

    # Áp dụng pyin để trích xuất tần số (pitches) và loại bỏ các giá trị None hoặc NaN
    pitches, voiced_flags, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    times = librosa.frames_to_time(np.arange(len(pitches)), sr=sr)

    results = []
    for pitch, time in zip(pitches, times):
        if pitch is not None and not math.isnan(pitch):  # Skip invalid values
            midi_number = round(69 + 12 * np.log2(pitch / 440.0))
            note_name = midi_to_note_name(midi_number)
            results.append({"time": round(time, 2), "note": note_name})

    # Lưu kết quả vào thư mục data
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, "user_voice_notes.json")
    with open(output_file, "w") as f:
        json.dump(results, f, separators=(",", ":"))

    print(f"File saved to {output_file}")
