# チュートリアル動画ワークフロー

スクリーンキャスト・解説動画に特化したワークフロー。
章ごとに分けて収録した動画に対して、同じワークフローを繰り返し適用する想定。

## 想定シナリオ

- 録画ツール: StreamYard（1人での画面共有収録）
- 録画形式: MP4（WebRTC 経由、48kHz 音声）
- 課題: (1)無音・言い直し部分が多い (2)周囲の人の会話が入っている（コワーキングスペース等）
- 出力: YouTube 向け MP4

## 入力ファイルの特徴（StreamYard）

StreamYard は WebRTC ベースの録画のため、以下の特徴がある：

- 音声は WebRTC の圧縮を通過しており、純粋な PCM 録音より音質が劣る
- 画面共有の映像はスクリーン + ワイプカメラの合成レイアウト
- ローカル録画を有効にしている場合は個別トラック（高品質）が利用可能

**ローカル録画が利用可能な場合はそちらを優先して使うこと。**

## 作業ディレクトリの準備

```bash
PROJECT="tutorial_$(date +%Y%m%d)"
mkdir -p "$PROJECT"/{input,cleaned,clips,output}
# 章ごとの動画ファイルを input/ に配置
# 例: input/01_setup.mp4, input/02_twig_basics.mp4, ...
cd "$PROJECT"
```

## Step 1: ノイズ除去（最初に必ずやる）

周囲の人の会話が入っている場合は **demucs**（音声分離）が最も効果的。
エアコン音など一定のノイズだけなら noisereduce や ffmpeg でも十分。

```bash
# 推奨: 周囲の会話を除去する場合（demucs）
python3 ${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py \
  input/01_setup.mp4 \
  cleaned/01_setup.mp4 \
  --method demucs

# 代替: 一定のノイズ（エアコン等）だけの場合（noisereduce）
python3 ${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py \
  input/01_setup.mp4 \
  cleaned/01_setup.mp4 \
  --method noisereduce \
  --noise-start 0.0 \
  --noise-end 2.0

# 軽量: 追加依存なし、すぐ試したい場合（ffmpeg フィルター）
python3 ${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py \
  input/01_setup.mp4 \
  cleaned/01_setup.mp4 \
  --method ffmpeg
```

### ノイズ除去手法の選び方

| 状況 | 推奨手法 | 理由 |
|------|---------|------|
| 周囲の人の会話が入っている | `--method demucs` | 人の声を分離できる唯一の手法 |
| エアコン・機器の一定ノイズ | `--method noisereduce` | 定常ノイズに強い |
| 軽いノイズ、すぐ試したい | `--method ffmpeg` | 追加インストール不要 |

**確認**: 出力を再生して声が不自然になっていないか確認する。
- demucs で声がこもる → noisereduce に切り替え
- noisereduce でロボット声 → ffmpeg に切り替え

## Step 2: 無音・言い直し部分の自動カット

```bash
# 無音区間を検出（閾値を環境に合わせて調整）
ffmpeg -i cleaned/01_setup.mp4 \
  -af silencedetect=noise=-35dB:d=0.8 \
  -f null - 2>&1 | grep silence
```

**閾値の目安**:
- `-30dB:d=0.5`: 短い間も積極的にカット（テンポよく仕上がる）
- `-35dB:d=0.8`: 標準設定（自然な間を残す）
- `-40dB:d=1.0`: 間を残す（ゆったりした解説向け）

```bash
# 自動カット実行
python3 ${CLAUDE_SKILL_DIR}/../ffmpeg-edit/references/cutting.py \
  cleaned/01_setup.mp4 \
  clips/01_setup.mp4
```

**手動カット（言い直し部分）**:

Whisper の transcript を見て「言い直し」の秒数を特定し、keep_segments.txt に書く:

```bash
# まず transcript を確認
ffmpeg -i cleaned/01_setup.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio_tmp.wav
python3 -c "
from faster_whisper import WhisperModel

model = WhisperModel('large-v3', device='cpu', compute_type='int8')
segments, _ = model.transcribe('audio_tmp.wav', language='ja')

for s in segments:
    print(f'[{s.start:.1f}s-{s.end:.1f}s] {s.text}')
" > transcript.txt
rm audio_tmp.wav

cat transcript.txt  # 内容を確認して言い直し部分の秒数をメモ
```

## Step 3: YouTube 向け書き出し

```bash
ffmpeg -i clips/01_setup.mp4 \
  -vcodec libx264 -crf 23 \
  -vf "scale=-2:1080" \
  -acodec aac -b:a 192k \
  -movflags +faststart \
  output/01_setup.mp4
```

## Step 4: 完成確認

```bash
ffprobe -v quiet -show_entries format=duration,size \
  -of default=noprint_wrappers=1 output/01_setup.mp4

open output/01_setup.mp4  # macOS
```

## 複数動画のバッチ処理

章ごとに同じワークフローを繰り返す場合、以下のシェルスクリプトで一括処理できる：

```bash
#!/bin/bash
DENOISE_SCRIPT="${CLAUDE_SKILL_DIR}/../noise-clean/scripts/denoise.py"
CUTTING_SCRIPT="${CLAUDE_SKILL_DIR}/../ffmpeg-edit/references/cutting.py"

for input_file in input/*.mp4; do
  name=$(basename "$input_file" .mp4)
  echo "=== 処理中: $name ==="

  # Step 1: ノイズ除去
  python3 "$DENOISE_SCRIPT" "$input_file" "cleaned/${name}.mp4" --method demucs

  # Step 2: 無音カット
  python3 "$CUTTING_SCRIPT" "cleaned/${name}.mp4" "clips/${name}.mp4"

  # Step 3: YouTube 向け書き出し
  ffmpeg -y -i "clips/${name}.mp4" \
    -vcodec libx264 -crf 23 \
    -vf "scale=-2:1080" \
    -acodec aac -b:a 192k \
    -movflags +faststart \
    "output/${name}.mp4"

  echo "=== 完了: output/${name}.mp4 ==="
done
```

## オプション: 字幕生成

字幕が必要な場合は `whisper-caption` スキルを使って SRT を生成できる。

```bash
# カット済みファイルから音声抽出
ffmpeg -i clips/01_setup.mp4 \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  audio.wav

# Whisper で文字起こし + SRT 生成
python3 -c "
from faster_whisper import WhisperModel

def fmt(t):
    h,m=int(t//3600),int((t%3600)//60)
    s,ms=int(t%60),int((t%1)*1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

model = WhisperModel('large-v3', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio.wav', language='ja', vad_filter=True)
segments = list(segments)

with open('output/01_setup.srt', 'w', encoding='utf-8') as f:
    for i, seg in enumerate(segments, 1):
        f.write(f'{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n\n')

print(f'字幕セグメント数: {len(segments)}')
"
rm audio.wav
```

YouTube は SRT を直接アップロードできるので焼き込み不要。

### a-blog cms 用語の認識精度を上げる

```python
segments, info = model.transcribe(
    "audio.wav",
    language="ja",
    initial_prompt="a-blog cms、Twig、テンプレート、エントリー、モジュール、テーマ、カスタムフィールド、ブロック、インクルード"
)
```

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| 周囲の声が残っている | demucs で分離しきれない | demucs → noisereduce を2段階で適用する |
| ノイズ除去後に声がこもる | 除去が強すぎる | `--method ffmpeg` に切り替える |
| カット後に音が飛ぶ | `-c copy` のキーフレーム問題 | cutting.py の `--fast-copy` を外す（デフォルトは再エンコード） |
| StreamYard の音声が劣化している | WebRTC 圧縮 | ローカル録画を有効にして高品質トラックを使う |
| a-blog cms 用語の誤認識 | 固有名詞 | Whisper に `initial_prompt` で用語を事前投入する |
