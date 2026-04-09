# チュートリアル動画ワークフロー

スクリーンキャスト・解説動画（a-blog CMS チュートリアルなど）に特化したワークフロー。

## 想定シナリオ

- 録画環境: Mac スクリーンキャスト（QuickTime / Loom / OBS）
- 課題: (1)無音・言い直し部分が多い (2)オフィスの環境音が入っている
- 出力: YouTube または社内共有用 MP4

## Step 1: ノイズ除去（最初に必ずやる）

```bash
# 録画の最初の 2 秒が無音・環境音だけの場合（推奨）
python3 ${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py \
  input/tutorial.mp4 \
  cleaned/tutorial_clean.mp4 \
  --method noisereduce \
  --noise-start 0.0 \
  --noise-end 2.0

# 最初から声が入っている場合（ノイズサンプルなし）
python3 ${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py \
  input/tutorial.mp4 \
  cleaned/tutorial_clean.mp4 \
  --method ffmpeg
```

**確認**: 出力を再生して声が不自然になっていないか確認する。
もし「ロボット声」になっていたら `--method ffmpeg` に切り替える。

## Step 2: 無音・言い直し部分の自動カット

```bash
# 無音区間を検出（閾値を環境に合わせて調整）
ffmpeg -i cleaned/tutorial_clean.mp4 \
  -af silencedetect=noise=-35dB:d=0.8 \
  -f null - 2>&1 | grep silence
```

**閾値の目安**:
- `-30dB:d=0.5`: 短い間も積極的にカット（テンポよく仕上がる）
- `-35dB:d=0.8`: 標準設定（自然な間を残す）
- `-40dB:d=1.0`: 間を残す（ゆったりした解説向け）

```bash
# 自動カット実行（cutting.py を使う）
python3 ${CLAUDE_SKILL_DIR}/../ffmpeg-edit/references/cutting.py \
  cleaned/tutorial_clean.mp4 \
  clips/tutorial_cut.mp4
```

**手動カット（言い直し部分）**:

Whisper の transcript を見て「言い直し」の秒数を特定し、keep_segments.txt に書く:

```bash
# まず transcript を確認
python3 -c "
from faster_whisper import WhisperModel
import json

model = WhisperModel('large-v3', device='cpu', compute_type='int8')
segments, _ = model.transcribe('audio/tutorial.wav', language='ja')

for s in segments:
    print(f'[{s.start:.1f}s-{s.end:.1f}s] {s.text}')
" > transcript.txt

cat transcript.txt  # 内容を確認して言い直し部分の秒数をメモ
```

```bash
# keep_segments.txt に残す区間を書く（言い直し前の秒を end に指定）
# 例: 15秒で言い直しがあった場合、14.5s で区間を切る
cat > keep_segments.txt << 'EOF'
0 14.5
16.8 45.0
47.0 120.0
EOF
```

## Step 3: 文字起こし・字幕生成

```bash
# カット済みファイルから音声抽出
ffmpeg -i clips/tutorial_cut.mp4 \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  audio/tutorial.wav

# Whisper で文字起こし + SRT 生成
python3 -c "
from faster_whisper import WhisperModel

def fmt(t):
    h,m=int(t//3600),int((t%3600)//60)
    s,ms=int(t%60),int((t%1)*1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

model = WhisperModel('large-v3', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio/tutorial.wav', language='ja', vad_filter=True)
segments = list(segments)

with open('captions/captions.srt', 'w', encoding='utf-8') as f:
    for i, seg in enumerate(segments, 1):
        f.write(f'{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n\n')

print(f'字幕セグメント数: {len(segments)}')
print('出力: captions/captions.srt')
"
```

## Step 4: 字幕の確認・修正

```bash
# SRT の内容を確認
cat captions/captions.srt

# テキストエディタで誤認識を修正
# （a-blog CMS 固有の用語が誤認識されやすい）
# 例: "エントリー" → 正しく認識されるはず
#     "モジュール" → 正しく認識されるはず
#     "テーマ" → 正しく認識されるはず
```

## Step 5: 字幕焼き込み + 書き出し

### オプション A: シンプル焼き込み（推奨・最速）

```bash
ffmpeg -i clips/tutorial_cut.mp4 \
  -vf "subtitles=captions/captions.srt:force_style='FontName=Noto Sans CJK JP,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" \
  -vcodec libx264 -crf 23 \
  -acodec aac -b:a 192k \
  output/tutorial_final.mp4
```

### オプション B: 字幕なし（YouTube に SRT を別途アップロード）

```bash
# YouTube は SRT を直接アップロードできるので焼き込みなしでもOK
ffmpeg -i clips/tutorial_cut.mp4 \
  -vcodec libx264 -crf 23 \
  -vf "scale=-2:1080" \
  -acodec aac -b:a 192k \
  -movflags +faststart \
  output/tutorial_final.mp4

# SRT は output/ にコピーしておく
cp captions/captions.srt output/tutorial_captions.srt
```

## Step 6: 完成確認

```bash
# ファイルサイズ・長さを確認
ffprobe -v quiet -show_entries format=duration,size -of default=noprint_wrappers=1 output/tutorial_final.mp4

# 再生確認
open output/tutorial_final.mp4  # macOS
```

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| ノイズ除去後に声がこもる | prop_decrease が高すぎる | `--method ffmpeg` に切り替えるか noisereduce の prop_decrease を 0.6 に下げる |
| カット後に音が飛ぶ | `-c copy` のキーフレーム問題 | カット時に `-c copy` を外す |
| 字幕がずれている | カット後の秒数が合っていない | カット済みファイルに対して改めて Whisper を実行 |
| a-blog CMS 用語の誤認識 | 固有名詞 | SRT を手動修正、または Whisper に `initial_prompt` を渡す |

## Whisper に a-blog CMS 用語を事前に教える

```python
segments, info = model.transcribe(
    "audio/tutorial.wav",
    language="ja",
    initial_prompt="a-blog CMS、エントリー、モジュール、テーマ、カスタムフィールド、ブロック、インクルード"
)
```
