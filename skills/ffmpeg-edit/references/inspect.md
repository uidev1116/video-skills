# 動画情報取得・フレーム抽出

## 動画情報を JSON で取得する
```bash
ffprobe -v quiet -print_format json -show_streams -show_format input.mp4
```

## 長さだけ取得する
```bash
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
```

## 解像度・FPS だけ取得する
```bash
ffprobe -v quiet -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate \
  -of default=noprint_wrappers=1 input.mp4
```

## サムネイルを取得する（1秒目）
```bash
ffmpeg -i input.mp4 -ss 00:00:01 -frames:v 1 thumbnail.jpg
```

## 一定間隔でフレームを抽出する（5秒ごと）
```bash
mkdir -p frames
ffmpeg -i input.mp4 -vf "fps=1/5" frames/frame_%04d.jpg
```
