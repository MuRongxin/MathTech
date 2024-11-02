import librosa
import numpy as np

def analyze_tempo(file_path):
   audio, sr = librosa.load(file_path)
   print("音频采样率: ", sr)
   onset_env = librosa.onset.onset_strength(audio, sr=sr)
   print("onset_env: ", onset_env)
   tempo = librosa.beat.tempo(onset_env, sr=sr)
   print("音乐节奏: ", tempo)
   return tempo[0]

if __name__ == "__main__":
   file_path = "../bgm.mp3"
   tempo = analyze_tempo(file_path)
   print("音乐节奏: ", tempo) 

   生活不可能像你想象得那么好，但也不会像你想象得
   那么糟。我觉得人的脆弱和坚强都超乎自己的想象。有时，我可能脆弱得一句话就泪流满面，有时，也发现自己咬着牙走了很长的路。
