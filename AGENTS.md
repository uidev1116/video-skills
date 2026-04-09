# 動画編集スキル

このプロジェクトは動画編集を自律実行するためのエージェントスキルを提供します。4つのスキルがインストールされています。

## スキルの選び方

- **動画のカット・トリム・結合・変換・情報取得** -- `ffmpeg-edit` スキルを使う
- **音声の文字起こし・字幕（SRT/VTT）生成** -- `whisper-caption` スキルを使う
- **背景ノイズ・環境音の除去** -- `noise-clean` スキルを使う
- **複数ステップのワークフローを一括実行** -- `video-pipeline` スキルを使う

## 重要なルール

- 編集を始める前に必ず `ffprobe` で入力ファイルの情報を確認する
- ノイズ除去はカットの*前*に行う -- カット後にノイズ除去するとカット点でアーティファクトが出る
- Whisper に渡す前に音声を WAV 16kHz モノラルに変換する: `ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav`
- 文字起こし時は `vad_filter=True` と明示的な `language="ja"`（または `"en"`）を指定して精度を上げる
- 無音検出の閾値 `noise=-35dB:d=0.8` は録音環境に合わせて調整する（静かな部屋ではより低い閾値が必要）
- `-c copy` でカットするとキーフレーム精度になる -- フレーム単位の正確さが必要なら `-c copy` を外す
- 音量は YouTube/SNS 向けに -14 LUFS、Podcast 向けに -16 LUFS にノーマライズする
- `noisereduce` でロボット声になる場合は `--method ffmpeg` に切り替える
- a-blog cms チュートリアルでは Whisper に `initial_prompt` で用語を事前投入して認識精度を上げる
- パイプラインワークフローでは作業ディレクトリ構造（`input/`, `cleaned/`, `clips/`, `audio/`, `captions/`, `output/`）を作成する
