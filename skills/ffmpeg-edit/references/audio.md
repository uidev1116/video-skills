# 音声処理の詳細

## 音量ノーマライズ（YouTube 推奨: -14 LUFS）

```bash
# 2パス loudnorm（推奨）
# Step 1: 測定
ffmpeg -i input.mp4 -af loudnorm=I=-14:LRA=11:TP=-1:print_format=json -f null - 2>&1

# Step 2: 測定値を使って変換（measured_* の値を入れる）
ffmpeg -i input.mp4 -af \
  "loudnorm=I=-14:LRA=11:TP=-1:measured_I=-18.2:measured_LRA=7.4:measured_TP=-3.1:measured_thresh=-28.5:linear=true" \
  output_normalized.mp4
```

SNS向けターゲット:
- YouTube: -14 LUFS
- Instagram / TikTok: -14 LUFS
- Podcast: -16 LUFS

## 音量を単純に上げ下げする

```bash
# 2倍にする
ffmpeg -i input.mp4 -af "volume=2.0" output.mp4

# -6dB 下げる
ffmpeg -i input.mp4 -af "volume=-6dB" output.mp4
```

## BGM と声をミックスする

```bash
# 声はそのまま、BGM を -20dB に下げてミックス
ffmpeg -i voice.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=-20dB[bgm];[0:a][bgm]amix=inputs=2:duration=first" \
  -c:v copy output_with_bgm.mp4
```

## 音声だけを差し替える

```bash
ffmpeg -i video.mp4 -i new_audio.mp3 \
  -c:v copy -c:a aac \
  -map 0:v:0 -map 1:a:0 \
  output.mp4
```
