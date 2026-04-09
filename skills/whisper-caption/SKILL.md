---
name: whisper-caption
description: >
  Use this skill whenever audio or video content needs to be transcribed,
  captioned, or converted to subtitle files. Always trigger on: 文字起こし,
  字幕を作って, transcribe, captions, SRT, VTT, "何を言っているか文字にして",
  "テキストに書き起こして", "subtitle", "closed captions".
  Also trigger proactively when video-pipeline is running and captions
  haven't been generated yet — don't wait for the user to ask.
  Handles: Japanese, English, and multilingual content.
  Output formats: plain text, SRT, VTT, word-level JSON.
  Do NOT trigger for AI voice/narration generation (→ elevenlabs-tts skill).
  Requires: Python 3.9+, faster-whisper (recommended) or openai-whisper.
---

# whisper-caption

Whisper を使った文字起こし・字幕ファイル生成スキル。

## セットアップ

```bash
# faster-whisper（推奨：M4 Mac で高速）
pip install faster-whisper

# または openai-whisper（オリジナル）
pip install openai-whisper
```

## 音声の前処理（動画ファイルの場合）

```bash
# Whisper は WAV 16kHz モノラルが最も精度が出る
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

## 文字起こし（SRT も同時出力）

```python
from faster_whisper import WhisperModel

def transcribe(audio_path, language="ja", model_size="large-v3"):
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,          # 無音区間を自動スキップ
        vad_parameters={
            "min_silence_duration_ms": 500
        }
    )
    return list(segments), info

def save_srt(segments, output_path):
    def fmt(t):
        h, m = int(t // 3600), int((t % 3600) // 60)
        s, ms = int(t % 60), int((t % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n\n")

# 実行
segments, info = transcribe("audio.wav")
save_srt(segments, "captions.srt")
print(f"言語: {info.language}、セグメント数: {len(segments)}")
```

## 言語別の推奨設定

| 言語 | language= | 推奨モデル |
|------|----------|-----------|
| 日本語 | "ja" | large-v3 |
| 英語 | "en" | large-v3 または base |
| 自動判定 | None | large-v3 |

## モデル選択とファイルサイズ

詳細は [references/models.md](references/models.md) を参照。

## SRT フォーマットの詳細

詳細は [references/srt_format.md](references/srt_format.md) を参照。

## 他のスキルとの連携

- 字幕を動画に焼き込む → `ffmpeg-edit`（`subtitles=` フィルター）
- アニメーション字幕（Remotion）→ `remotion-best-practices` の rules/subtitles.md
- 全工程一括実行 → `video-pipeline`
