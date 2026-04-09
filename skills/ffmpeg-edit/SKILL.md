---
name: ffmpeg-edit
description: >
  Use this skill whenever FFmpeg is needed to edit, cut, trim, merge, or
  convert video or audio files. Always trigger on: cut a clip, trim video,
  merge/concat multiple videos, extract audio, convert format (mp4/mov/webm),
  add audio to video, get video info/metadata, detect silence, adjust volume,
  burn-in subtitles. Also trigger when "動画をカット", "音声を抽出",
  "mp4に変換", "動画を結合", "無音を削除" appears in the request.
  Trigger even when the user doesn't say "FFmpeg" — if it's a video file
  manipulation task without AI generation, this skill applies.
  Do NOT trigger for: AI video generation (→ ai-video-generation skill),
  Remotion React compositions (→ remotion-best-practices),
  transcription/captions (→ whisper-caption),
  noise removal (→ noise-clean).
---

# ffmpeg-edit

FFmpeg を使った動画・音声ファイルの操作スキル。

## 事前確認

```bash
ffmpeg -version   # >= 4.0 必要
ffprobe -version  # ffmpeg と同梱
```

インストール: `brew install ffmpeg` (Mac) / `sudo apt install ffmpeg` (Ubuntu)

## よく使うコマンド（インライン）

### 動画情報を取得する
```bash
ffprobe -v quiet -print_format json -show_streams -show_format input.mp4
```

### 特定区間をカットする
```bash
# 高速（キーフレーム精度、ズレが出ることある）
ffmpeg -i input.mp4 -ss 00:01:10 -to 00:02:45 -c copy output.mp4

# 正確（再エンコード、遅いが正確）
ffmpeg -i input.mp4 -ss 00:01:10 -to 00:02:45 output.mp4
```

### 複数クリップを結合する
```bash
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\nfile 'clip3.mp4'" > filelist.txt
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

### 音声を抽出する（Whisper 用に WAV 変換）
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

### 無音区間を検出する
```bash
ffmpeg -i input.mp4 -af silencedetect=noise=-35dB:d=0.8 -f null - 2>&1 | grep silence
```
※ noise=-35dB（閾値）と d=0.8（最短秒数）は環境に合わせて調整する

### 字幕をハードサブ（焼き込み）する
```bash
ffmpeg -i input.mp4 -vf subtitles=captions.srt output_subbed.mp4
```

## 詳細リファレンス

複雑な操作が必要な場合は以下を読んでください：

- カット・分割・結合の詳細 → [references/cutting.md](references/cutting.md)
- 音声処理（音量調整・ノーマライズ・ミックス）→ [references/audio.md](references/audio.md)
- トランスコード・フォーマット変換 → [references/transcode.md](references/transcode.md)
- 動画情報取得・フレーム抽出 → [references/inspect.md](references/inspect.md)

## 他のスキルとの連携

| 次のステップ | 使うスキル |
|-------------|-----------|
| 文字起こし・字幕生成 | `whisper-caption` |
| ノイズ除去 | `noise-clean` |
| 全工程をまとめて実行 | `video-pipeline` |
| アニメーション字幕 | `remotion-best-practices` |
