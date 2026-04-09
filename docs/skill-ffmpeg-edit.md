# ffmpeg-edit スキル設計

## 概要

FFmpeg を使った動画・音声ファイルの操作スキル。カット、トリム、結合、トランスコード、音声抽出、字幕焼き込みなどを扱う。

## トリガー条件

ユーザーが明示的に "FFmpeg" と言わなくても、動画ファイルの操作タスク（AI 生成以外）であればこのスキルが適用される。

### トリガーするキーワード

- cut a clip, trim video, merge/concat, extract audio, convert format
- 動画をカット, 音声を抽出, mp4に変換, 動画を結合, 無音を削除
- get video info/metadata, detect silence, adjust volume, burn-in subtitles

### トリガーしないケース

| ケース | 代わりに使うスキル |
|--------|-----------------|
| AI 動画生成 | ai-video-generation |
| Remotion コンポジション | remotion-best-practices |
| 文字起こし・字幕 | whisper-caption |
| ノイズ除去 | noise-clean |

## SKILL.md の構成

SKILL.md 本文には以下のインラインコマンドを記載：

- 動画情報取得（`ffprobe`）
- 区間カット（高速 `-c copy` / 正確・再エンコード）
- 複数クリップ結合（concat）
- 音声抽出（Whisper 用 WAV 変換）
- 無音区間検出（`silencedetect`）
- 字幕ハードサブ

## references/ の構成

| ファイル | 内容 |
|---------|------|
| `cutting.md` | 無音検出からカット点計算、言い直しカット、エラー対処 |
| `cutting.py` | 無音カットの Python スクリプト（CLI 対応） |
| `audio.md` | 音量ノーマライズ（LUFS）、音量調整、BGM ミックス、音声差し替え |
| `transcode.md` | プラットフォーム別推奨エンコード設定、GIF 変換、CRF 目安 |
| `inspect.md` | JSON メタデータ取得、長さ・解像度取得、サムネイル・フレーム抽出 |

## cutting.py の設計

`cutting.py` は無音区間を検出して発話部分だけを切り出し・結合するスクリプト。

### 主要パラメータ

| パラメータ | デフォルト | 説明 |
|-----------|----------|------|
| `--noise-db` | -35 | 無音判定の閾値 dB |
| `--min-silence` | 0.8 | 最短無音長（秒） |
| `--fast-copy` | off | `-c copy` で高速カット（キーフレーム精度） |

### 動作フロー

1. `ffmpeg silencedetect` で無音区間を検出
2. 無音区間の逆（発話区間）を計算
3. 各発話区間を個別のクリップとして切り出し
4. `ffmpeg concat` で結合
