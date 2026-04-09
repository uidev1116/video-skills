# Whisper モデル選択ガイド

## faster-whisper モデル比較

| モデル | ダウンロードサイズ | RAM使用量 | 日本語精度 | 速度 |
|--------|-----------------|----------|-----------|------|
| tiny | 39 MB | ~200MB | △ | ◎◎ |
| base | 74 MB | ~300MB | ○ | ◎ |
| small | 244 MB | ~500MB | ○ | ○ |
| medium | 769 MB | ~1.5GB | ◎ | △ |
| large-v3 | 1.5 GB | ~3GB | ◎◎ | △△ |
| large-v3-turbo | 809 MB | ~1.5GB | ◎◎ | ○ |

**M4 Mac 推奨**: `large-v3` with `compute_type="int8"`
→ int8 量子化で速度が 2〜3 倍になり、精度はほぼ変わらない。

## M4 Mac での最速設定

```python
from faster_whisper import WhisperModel

# int8 量子化 + CPU（M4 の場合 GPU より安定することが多い）
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

# Apple Silicon GPU を使いたい場合（faster-whisper 1.0+ 対応）
# model = WhisperModel("large-v3", device="auto", compute_type="int8")
```

## 処理時間の目安（M4 MacBook Pro、large-v3 int8）

| 動画の長さ | 処理時間 |
|-----------|---------|
| 5分 | ~30秒 |
| 15分 | ~90秒 |
| 30分 | ~3分 |
| 60分 | ~6分 |

## モデルのキャッシュ場所

```bash
# キャッシュ場所を確認
ls ~/.cache/huggingface/hub/

# 容量が心配な場合は別ディレクトリを指定
model = WhisperModel("large-v3", download_root="/path/to/models", ...)
```

## 精度を上げるヒント

1. **音声の前処理が最重要**: ノイズが多い場合は先に `noise-clean` スキルを使う
2. **VAD フィルターを有効にする**: `vad_filter=True` で無音部分をスキップして精度向上
3. **言語を明示する**: `language="ja"` のように指定すると精度が上がる
4. **音量が小さい場合**: ffmpeg で正規化してから渡す
   ```bash
   ffmpeg -i input.wav -af loudnorm=I=-14:LRA=11:TP=-1 normalized.wav
   ```
