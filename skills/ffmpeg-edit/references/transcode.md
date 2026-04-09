# トランスコード・フォーマット変換

## プラットフォーム別推奨設定

### YouTube / 一般的な MP4
```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 23 -preset medium \
  -vf "scale=-2:1080" \
  -acodec aac -b:a 192k \
  output_1080p.mp4
```

### Instagram Reels / TikTok（縦動画）
```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 23 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -acodec aac -b:a 192k \
  output_reels.mp4
```

### X (Twitter) 対応
```bash
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 23 \
  -vf "scale=-2:720" \
  -acodec aac -b:a 128k \
  -movflags +faststart \
  output_twitter.mp4
```

### WebM（軽量・ブラウザ向け）
```bash
ffmpeg -i input.mp4 \
  -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -c:a libopus \
  output.webm
```

## GIF に変換する（サムネイル・プレビュー用）
```bash
# パレット生成 → GIF 変換（高品質）
ffmpeg -i input.mp4 -ss 0 -t 5 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -ss 0 -t 5 \
  -lavfi "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
```

## CRF 値の目安（libx264）

| CRF | 画質 | ファイルサイズ |
|-----|------|--------------|
| 18  | 高品質（ほぼロスレス） | 大 |
| 23  | 標準（YouTube推奨） | 中 |
| 28  | やや劣化 | 小 |
| 35  | SNS軽量化用 | 最小 |
