import os
import wave

def check_audio_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            filepath = os.path.join(directory, filename)
            try:
                with wave.open(filepath, 'rb') as audio_file:
                    frames = audio_file.getnframes()
            except wave.Error:
                print(f"Corrupted or incomplete audio file: {filepath}")
            except Exception as e:
                print(f"Error processing audio file: {filepath}")
                print(e)


# 指定目标目录进行检查
directory = r'dataset_raw/Y2Mate_Vocals/'
check_audio_files(directory)
