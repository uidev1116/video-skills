# video-skills

動画編集のための AI エージェントスキル -- FFmpeg によるカット・結合、Whisper による字幕生成、ノイズ除去、一括パイプライン。

## スキル一覧

| スキル | 機能 | トリガー条件 | Refs |
|---|---|---|:---:|
| **[ffmpeg-edit](skills/ffmpeg-edit/)** | カット・トリム・結合・トランスコード・音声抽出・字幕焼き込み | 動画ファイル操作全般 -- "動画をカット", "mp4に変換", "動画を結合", 無音検出 | cutting, audio, transcode, inspect |
| **[whisper-caption](skills/whisper-caption/)** | 文字起こし・SRT/VTT 字幕生成 | "文字起こし", "字幕を作って", transcribe, captions, SRT | models, srt_format |
| **[noise-clean](skills/noise-clean/)** | FFmpeg フィルター / noisereduce / Demucs による背景ノイズ除去 | "ノイズを消して", "背景音を除去", "エアコンの音", 録音環境の言及 | audio_filters |
| **[video-pipeline](skills/video-pipeline/)** | 上記3つを束ねるオーケストレーター | 2ステップ以上のタスク -- "チュートリアル動画を仕上げたい", "ノイズ消してカットして字幕もつけて" | tutorial_workflow, platform_presets |

## インストール

### Claude Code プラグイン（GitHub から追加）

本リポジトリは [Claude Code プラグイン](https://code.claude.com/docs/plugins)としてインストールできます。スキルは `video-skills:` 名前空間で自動認識されます。

```shell
# 1. マーケットプレイスとして追加
/plugin marketplace add uidev1116/video-skills

# 2. プラグインをインストール
/plugin install video-skills@uidev1116-video-skills
```

ローカルでのテスト：

```bash
claude --plugin-dir /path/to/video-skills
```

### Vercel's Skills CLI

```bash
npx skills add uidev1116/video-skills
```

### 手動インストール

スキルディレクトリを手動でコピーすることもできます：

```bash
# Claude Code（プロジェクト単位、git で共有）
mkdir -p .claude/skills && cp -r skills/* .claude/skills/

# Claude Code（ユーザー単位、全プロジェクトで利用可能）
cp -r skills/* ~/.claude/skills/
```

必要に応じてコンテキストファイルをプロジェクトルートにコピーしてください：

```bash
cp CLAUDE.md /path/to/project/   # Claude Code
cp AGENTS.md /path/to/project/   # OpenAI Codex
```

## 仕組み

各スキルは **Progressive Disclosure** パターンで情報を段階的に開示します：

1. **Description**（YAML frontmatter）-- 常に読み込まれ、スキルを*いつ*使うか判断する材料になる
2. **SKILL.md 本文** -- スキル呼び出し時に読み込まれる。よく使うコマンドと基本手順
3. **references/** -- 必要に応じてオンデマンドで読み込まれる。詳細リファレンスとトラブルシューティング

エージェントは必要な情報だけを取得し、コンテキストウィンドウの消費を抑えます。

[Agent Skills](https://agentskills.io/specification) オープンスタンダードに準拠。

## 必要な環境

- **FFmpeg** 4.0+（`brew install ffmpeg` / `sudo apt install ffmpeg`）
- **Python** 3.9+
- **faster-whisper**（`pip install faster-whisper`）-- 字幕生成用
- **noisereduce**（`pip install -r skills/noise-clean/scripts/requirements.txt`）-- ノイズ除去用

## コンテキストファイル

| ファイル | プラットフォーム |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | OpenAI Codex |

## リポジトリ構成

```
.
├── .claude-plugin/
│   └── plugin.json              # Claude Code プラグインマニフェスト
├── CLAUDE.md                    # Claude Code 向けコンテキスト
├── AGENTS.md                    # OpenAI Codex 向けコンテキスト
├── docs/                        # 設計ドキュメント
└── skills/
    ├── ffmpeg-edit/
    │   ├── SKILL.md
    │   └── references/
    │       ├── cutting.md
    │       ├── cutting.py
    │       ├── audio.md
    │       ├── transcode.md
    │       └── inspect.md
    ├── whisper-caption/
    │   ├── SKILL.md
    │   └── references/
    │       ├── models.md
    │       └── srt_format.md
    ├── noise-clean/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── denoise.py
    │   │   └── requirements.txt
    │   └── references/
    │       └── audio_filters.md
    └── video-pipeline/
        ├── SKILL.md
        └── references/
            ├── tutorial_workflow.md
            └── platform_presets.md
```

## オプションのプラグイン

- **remotion-best-practices** -- Remotion によるアニメーション字幕
- **elevenlabs-tts** -- AI ナレーション生成

## ライセンス

MIT
