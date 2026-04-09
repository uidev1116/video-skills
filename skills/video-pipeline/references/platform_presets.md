# プラットフォーム別書き出し設定

## YouTube（1080p・標準）

```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 20 -preset slow \
  -vf "scale=-2:1080" \
  -acodec aac -b:a 192k \
  -movflags +faststart \
  output_youtube.mp4
```

## YouTube Shorts / Instagram Reels（縦 9:16）

```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 23 \
  -vf "crop=ih*9/16:ih,scale=1080:1920" \
  -acodec aac -b:a 192k \
  output_shorts.mp4
```

## X (Twitter)（最大 512MB・2分20秒）

```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 28 \
  -vf "scale=-2:720" \
  -acodec aac -b:a 128k \
  -movflags +faststart \
  output_twitter.mp4
```

## 社内共有（軽量・高速）

```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 28 -preset fast \
  -vf "scale=-2:720" \
  -acodec aac -b:a 128k \
  output_share.mp4
```

## ファイルサイズの目安（1分あたり）

| 設定 | サイズ目安 |
|------|----------|
| CRF 18, 1080p | ~200MB |
| CRF 23, 1080p | ~80MB |
| CRF 23, 720p | ~40MB |
| CRF 28, 720p | ~20MB |
