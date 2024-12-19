import json
import os
import sys

def load_json(filepath):
    with open(filepath, "r") as file:
        return json.load(file)
    
def create_note_mapping():
    octaves = [2, 3, 4, 5, 6, 7]
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return {f"{note}{octave}": i + 12 * (octave - 2) for octave in octaves for i, note in enumerate(notes)}

NOTE_MAPPING = create_note_mapping()

def int_to_note_mapping():
    return {v: k for k, v in NOTE_MAPPING.items()}

INT_TO_NOTE_MAPPING = int_to_note_mapping()

def int_to_note(value):
    closest_int = round(value)
    return INT_TO_NOTE_MAPPING.get(closest_int, None)

def note_to_int(note):
    return NOTE_MAPPING.get(note, None)

def is_within_semitone_range(user_avg_note, song_note):
    song_note_value = note_to_int(song_note)
    if song_note_value is None or user_avg_note is None:
        return False
    return song_note_value - 1 <= round(user_avg_note) <= song_note_value + 1

def calculate_average_note(user_notes_in_range):
    note_values = [note_to_int(user_note["note"]) for user_note in user_notes_in_range if note_to_int(user_note["note"]) is not None]
    return sum(note_values) / len(note_values) if note_values else None

def compare_notes(song_notes, user_voice_data):
    matches = []
    for song_note in song_notes:
        start_time = song_note["start"]
        end_time = start_time + song_note["duration"]
        song_note_name = song_note["note"]
        lyric = song_note["lyric"]

        # Lấy các nốt trong khoảng thời gian này
        user_notes_in_range = [
            user_note for user_note in user_voice_data
            if start_time <= user_note["time"] <= end_time
        ]

        # Tính giá trị trung bình của các nốt nhạc người dùng
        user_avg_note = calculate_average_note(user_notes_in_range)

        # Kiểm tra nốt nhạc người dùng có khớp ±1/2 cung
        match = is_within_semitone_range(user_avg_note, song_note_name)

        actual_note = int_to_note(user_avg_note) if user_avg_note is not None else "No data"

        if (not match):
            matches.append({
                "start_time": start_time,
                "song_note": song_note_name,
                "actual_note": actual_note,
                "lyric": lyric
            })

    return matches

def compare_user_voice_with_score(template_file_path, user_file_path, result_file_path):
    # Đọc dữ liệu từ file template và user
    try:
        with open(template_file_path, 'r', encoding='utf-8') as template_file:
            template_data = json.load(template_file)
        print(f"Read file {template_file} success")
    except Exception as e:
        print(f"Error loading {template_file_path}: {e}")
        sys.exit(1)

    try:
        with open(user_file_path, 'r', encoding='utf-8') as user_file:
            user_data = json.load(user_file)
        print(f"Read file {user_file} success")
    except Exception as e:
        print(f"Error loading {user_file_path}: {e}")
        sys.exit(1)

    # So sánh các nốt nhạc
    errors = compare_notes(template_data, user_data)

    # Ghi kết quả vào file JSON
    os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
    try:
        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            # Ghi kết quả theo định dạng mong muốn
            result_output = []
            for result in errors:
            # Thêm từng kết quả vào danh sách
                result_output.append({
                    "time": result['start_time'],
                    "expected": result['song_note'],
                    "actual": result['actual_note'],
                    "lyric": result['lyric']
                })
            
            json.dump(result_output, result_file, ensure_ascii=False, indent=4)
            print(f"Kết quả đã được lưu vào {result_file_path}")
    except Exception as e:
        print(f"Error writing to {result_file_path}: {e}")
        sys.exit(1)