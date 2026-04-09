# whisper-caption スキル設計

## 概要

Whisper を使った文字起こし・字幕ファイル生成スキル。日本語・英語・多言語に対応し、SRT/VTT/JSON 形式で出力する。

## トリガー条件

### トリガーするキーワード

- 文字起こし, 字幕を作って, テキストに書き起こして
- transcribe, captions, SRT, VTT, subtitle, closed captions
- `video-pipeline` 実行中に字幕が未生成の場合は自動トリガー

### トリガーしないケース

| ケース | 代わりに使うスキル |
|--------|-----------------|
| AI 音声・ナレーション生成 | elevenlabs-tts |

## 依存ライブラリ

| ライブラリ | 推奨 | 備考 |
|-----------|------|------|
| faster-whisper | **推奨** | M4 Mac で高速、int8 量子化対応 |
| openai-whisper | 代替 | オリジナル実装 |

## SKILL.md の構成

- セットアップ手順（pip install）
- 音声前処理（WAV 16kHz モノラル変換）
- 文字起こし + SRT 出力の Python コード
- 言語別推奨設定の表

## references/ の構成

| ファイル | 内容 |
|---------|------|
| `models.md` | モデル比較表（サイズ・RAM・精度・速度）、M4 Mac 最速設定、処理時間目安、キャッシュ管理、精度向上ヒント |
| `srt_format.md` | SRT/VTT 仕様、SRT→VTT 変換、Remotion 向け JSON 出力、字幕品質の後処理 |

## 設計上のポイント

- **モデルは `large-v3` + `compute_type="int8"` を推奨**: 精度を落とさず速度 2-3 倍
- **VAD フィルターを標準で有効化**: 無音部分のスキップで精度向上
- **`initial_prompt` で固有名詞を事前投入可能**: a-blog CMS 等の用語認識改善
