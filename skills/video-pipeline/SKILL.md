---
name: video-pipeline
description: >
  Use this skill to plan and run a complete multi-step video editing workflow.
  Always trigger when the user describes a task with 2+ steps, such as:
  "録画した動画を編集して字幕をつけてYouTubeにアップできる形にして",
  "チュートリアル動画を仕上げたい", "edit and clean up this screencast",
  "ノイズ消してカットして字幕もつけて", "動画をまとめて処理して",
  "end-to-end video editing", "動画全部やっておいて".
  This skill orchestrates ffmpeg-edit, whisper-caption, and noise-clean
  together. Trigger even when the user doesn't say "pipeline" — any request
  that involves more than one video processing step should use this skill.
  Special workflows available:
  - tutorial_workflow: スクリーンキャスト・解説動画向け（ノイズ除去→カット→字幕）
  - For Remotion animations: also load remotion-best-practices after Step 4
---

# video-pipeline

FFmpeg + Whisper + ノイズ除去を束ねるオーケストレータースキル。

## まず状況を確認する

パイプラインを開始する前に以下を確認してください：

1. **入力ファイル**: パス・形式・時間の長さ
2. **目的**: カット編集のみ？字幕も？ノイズ除去も？
3. **出力先**: YouTube / SNS / 社内共有 / プレゼン
4. **Remotion 不要なら**: FFmpeg だけで完結できる

```bash
# まずファイル情報を確認する
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4 | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)
fmt=d['format']
print(f'時間: {float(fmt[\"duration\"]):.1f}秒')
print(f'サイズ: {int(fmt[\"size\"])//1024//1024}MB')
for s in d['streams']:
    if s['codec_type']=='video':
        print(f'映像: {s[\"width\"]}x{s[\"height\"]} {s[\"r_frame_rate\"]}fps')
    if s['codec_type']=='audio':
        print(f'音声: {s[\"codec_name\"]} {s.get(\"sample_rate\",\"?\")}Hz')
"
```

## ワークフロー選択

| ユースケース | 使うワークフロー |
|------------|---------------|
| スクリーンキャスト・チュートリアル動画 | [references/tutorial_workflow.md](references/tutorial_workflow.md) |
| SNS・YouTube 向けの短編動画 | Variant A（下記） |
| 字幕・アニメーションが必要な本格編集 | Variant B（下記） |

## Variant A: シンプル編集パイプライン

```
入力動画
  │
  ├─ Step 1: [noise-clean] ノイズ除去
  │    output: cleaned.mp4
  │
  ├─ Step 2: [ffmpeg-edit] 無音検出 → カット・結合（必要に応じて手動カットも）
  │    output: cut.mp4
  │
  ├─ Step 3: [ffmpeg-edit] 書き出し + プラットフォーム向けエンコード
  │    output: final.mp4
  │    詳細: references/platform_presets.md
  │
  └─ （オプション）[whisper-caption] 字幕が必要な場合
       output: captions.srt
```

## Variant B: 字幕付き編集パイプライン

```
入力動画
  │
  ├─ Step 1: [noise-clean] ノイズ除去
  │    output: cleaned.mp4
  │
  ├─ Step 2: [ffmpeg-edit] 無音検出 → カット・結合
  │    output: cut.mp4
  │
  ├─ Step 3: [whisper-caption] 文字起こし → SRT 生成
  │    output: captions.srt
  │
  ├─ Step 4: 字幕の確認・修正（固有名詞の誤認識など）
  │
  └─ Step 5: [ffmpeg-edit] 字幕焼き込み + 書き出し
       output: final.mp4
```

## Variant C: Remotion アニメーション字幕付き

Variant B の Step 4〜5 を差し替える：

```
  ├─ Step 4b: SRT を JSON に変換（word-level タイムスタンプ付き）
  ├─ Step 5b: [remotion-best-practices] Remotion コンポジション構築
  └─ Step 6b: npx remotion render でエンコード
```

## 作業ディレクトリの作成

```bash
PROJECT="my_video_$(date +%Y%m%d)"
mkdir -p "$PROJECT"/{input,cleaned,clips,audio,captions,output}
cp input.mp4 "$PROJECT/input/"
cd "$PROJECT"
```

## プラットフォーム書き出し設定

詳細は [references/platform_presets.md](references/platform_presets.md) を参照。

## よくある質問

**Q: どの Step から始めるべきか？**
A: ノイズが気になる場合は必ず Step 1（noise-clean）を最初に行う。
カット後にノイズ除去すると、カット点でアーティファクトが出ることがある。

**Q: 字幕の精度が低い場合は？**
A: ノイズ除去後の音声で再度 whisper-caption を実行すると改善する。

**Q: 処理が重くて時間がかかる場合は？**
A: 長い動画は `ffmpeg-edit` でカットしてから noise-clean・caption を実行する。
