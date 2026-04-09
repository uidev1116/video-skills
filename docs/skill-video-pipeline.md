# video-pipeline スキル設計

## 概要

ffmpeg-edit, whisper-caption, noise-clean を束ねるオーケストレータースキル。
複数ステップの動画編集ワークフローを計画・実行する。

## トリガー条件

2つ以上の動画処理ステップを含むタスクで自動トリガーされる。

### トリガーするキーワード

- 録画した動画を編集して字幕をつけてYouTubeにアップできる形にして
- チュートリアル動画を仕上げたい
- ノイズ消してカットして字幕もつけて
- 動画をまとめて処理して, 動画全部やっておいて
- edit and clean up this screencast, end-to-end video editing

## ワークフローバリアント

### Variant A: シンプル編集パイプライン

```
入力動画
  → Step 1: [noise-clean] ノイズ除去
  → Step 2: [ffmpeg-edit] 無音検出 → カット・結合
  → Step 3: [whisper-caption] 文字起こし → SRT 生成
  → Step 4: 字幕の確認・修正
  → Step 5: [ffmpeg-edit] 字幕焼き込み + 書き出し
  → Step 6: 完成確認 + プラットフォーム向けエンコード
```

### Variant B: Remotion アニメーション字幕付き

Step 4-5 を差し替え：SRT → JSON 変換 → Remotion コンポジション → render

## references/ の構成

| ファイル | 内容 |
|---------|------|
| `tutorial_workflow.md` | スクリーンキャスト・チュートリアル動画に特化した Step-by-Step ワークフロー。ノイズ除去 → カット → 字幕 → 書き出しの全手順、閾値チューニング、a-blog CMS 用語対応 |
| `platform_presets.md` | YouTube / YouTube Shorts / Instagram Reels / X / 社内共有の各プラットフォーム向け FFmpeg エンコード設定、ファイルサイズ目安 |

## 設計上のポイント

- **ノイズ除去は必ずカットの前に行う**: カット後にノイズ除去するとカット点でアーティファクトが出る
- **字幕精度はノイズ除去後に大幅向上**: ノイズ除去済み音声で Whisper を実行するのが推奨フロー
- **長い動画はカットしてから重い処理**: noise-clean や caption の処理時間を短縮するため
- **作業ディレクトリの構造を標準化**: `input/`, `cleaned/`, `clips/`, `audio/`, `captions/`, `output/`
