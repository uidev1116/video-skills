# SRT・VTT フォーマットと活用

## SRT フォーマット仕様

```
1
00:00:01,200 --> 00:00:04,500
こんにちは、今日は a-blog CMS の
インストール方法を解説します。

2
00:00:05,000 --> 00:00:08,300
まず、公式サイトからダウンロードします。

```

- 通し番号（1から始まる）
- タイムコード: `HH:MM:SS,mmm --> HH:MM:SS,mmm`（ミリ秒はカンマ区切り）
- 字幕テキスト（複数行可）
- 空行でセパレート

## VTT フォーマット（Web 用）

```
WEBVTT

00:00:01.200 --> 00:00:04.500
こんにちは、今日は a-blog CMS の
インストール方法を解説します。

00:00:05.000 --> 00:00:08.300
まず、公式サイトからダウンロードします。
```

SRT との違い: 先頭に `WEBVTT` が必要、タイムコードがピリオド区切り

## SRT から VTT へ変換する

```python
def srt_to_vtt(srt_path, vtt_path):
    with open(srt_path, encoding="utf-8") as f:
        content = f.read()
    # カンマをピリオドに変換
    content = content.replace(",", ".")
    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        # 行番号を除去してタイムコード行だけ残す
        lines = content.split("\n")
        for line in lines:
            # 数字のみの行（インデックス）は書かない
            if line.strip().isdigit():
                continue
            f.write(line + "\n")
```

## Remotion 向け JSON 出力（アニメーション字幕用）

```python
import json

def segments_to_json(segments, output_path):
    data = [
        {
            "index": i,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": [
                {"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3)}
                for w in (seg.words or [])
            ]
        }
        for i, seg in enumerate(segments)
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

word-level タイムスタンプを取得するには transcribe 時に `word_timestamps=True` を指定：

```python
segments, info = model.transcribe(audio_path, word_timestamps=True)
```

## 字幕の品質を上げる後処理

```python
def clean_segments(segments):
    """
    - 1行が長すぎる場合は分割
    - 不自然な句読点を修正
    """
    cleaned = []
    for seg in segments:
        text = seg.text.strip()
        # 空セグメントを除外
        if not text:
            continue
        # 40文字超えたら分割（日本語は短めに）
        if len(text) > 40:
            mid = len(text) // 2
            text = text[:mid] + "\n" + text[mid:]
        cleaned.append((seg.start, seg.end, text))
    return cleaned
```
