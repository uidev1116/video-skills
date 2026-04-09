---
name: noise-clean
description: >
  Use this skill to remove or reduce background noise, ambient sounds,
  or unwanted audio from video or audio files. Always trigger on:
  "ノイズを消して", "背景音を除去", "周りの声が入ってる", "環境音を消したい",
  "ミーティングの声が入ってしまった", "エアコンの音", "remove noise",
  "background noise", "clean up audio", "audio cleanup".
  Also trigger when the user mentions the recording environment
  (open office, cafe, outside) suggesting ambient noise is present.
  Two approaches available:
  1. FFmpeg filters: fast, no extra dependencies, moderate quality
  2. Demucs/noisereduce: slower, high quality, separates voice from noise
  Do NOT trigger for volume adjustment (→ ffmpeg-edit audio.md),
  or for replacing audio entirely (→ ffmpeg-edit audio.md).
---

# noise-clean

背景ノイズ・環境音の除去スキル。

## どちらのアプローチを使うか

| アプローチ | 速さ | 品質 | 向いているケース |
|-----------|------|------|----------------|
| FFmpeg フィルター | ◎ | ○ | エアコン音など一定の低周波ノイズ |
| noisereduce (Python) | ○ | ◎ | オフィス環境音全般 |
| Demucs | △ | ◎◎ | ミーティング中の他人の声が入っている |

## アプローチ 1: FFmpeg フィルター（追加インストール不要）

### 高周波ノイズ・シャーというノイズ
```bash
ffmpeg -i input.mp4 -af "highpass=f=200,lowpass=f=3000" output.mp4
```

### エアコン・室内の一定ノイズ（anlmdn）
```bash
ffmpeg -i input.mp4 -af "anlmdn=s=7:p=0.002:r=0.002:m=15" output.mp4
```

### 組み合わせ（推奨）
```bash
ffmpeg -i input.mp4 \
  -af "highpass=f=100,anlmdn=s=7:p=0.002:r=0.002:m=15,loudnorm=I=-14:LRA=11:TP=-1" \
  output_clean.mp4
```

## アプローチ 2: noisereduce Python スクリプト（推奨）

```bash
# セットアップ
pip install -r ${CLAUDE_SKILL_DIR}/scripts/requirements.txt

# 実行
python3 ${CLAUDE_SKILL_DIR}/scripts/denoise.py input.mp4 output_clean.mp4
```

詳細オプション:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/denoise.py input.mp4 output_clean.mp4 \
  --method noisereduce \    # noisereduce / demucs / ffmpeg
  --noise-start 0.0 \       # ノイズサンプル開始秒（最初の無音部分）
  --noise-end 2.0           # ノイズサンプル終了秒
```

## アプローチ 3: Demucs（他人の声が入っている場合）

```bash
pip install demucs

# 音声を「声」と「ノイズ」に分離する
demucs --two-stems=vocals input.wav -o output_dir/
# output_dir/htdemucs/input/vocals.wav  ← 声だけ
# output_dir/htdemucs/input/no_vocals.wav  ← それ以外（BGM含む）
```

注意: Demucs は音楽制作向けに設計されているため、
「ミーティング中の他人の声」は完全には除去できないが、大幅に低減できる。

## 詳細設定

[references/audio_filters.md](references/audio_filters.md) を参照してください。
