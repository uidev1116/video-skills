# ディレクトリ構成と設計方針

## プラグイン構成

本リポジトリは Claude Code プラグイン（`.claude-plugin/`）形式で構成している。
スキルは `skills/` サブディレクトリ配下に配置し、プラグインインストール時に
`video-skills:` 名前空間で自動的に認識される。

```
video-skills/
├── .claude-plugin/
│   └── plugin.json              # プラグインマニフェスト
├── AGENTS.md                    # OpenAI Codex 向けコンテキスト
├── docs/                        # 設計ドキュメント（本ディレクトリ）
└── skills/
    ├── ffmpeg-edit/
    │   ├── SKILL.md             # メイン指示（常に読み込まれる description + 基本コマンド）
    │   └── references/          # オンデマンド読み込み
    │       ├── cutting.md       # カット・分割・結合の詳細
    │       ├── cutting.py       # 無音カットスクリプト
    │       ├── audio.md         # 音量調整・ノーマライズ・ミックス
    │       ├── transcode.md     # フォーマット変換・プラットフォーム設定
    │       └── inspect.md       # メタデータ取得・フレーム抽出
    ├── whisper-caption/
    │   ├── SKILL.md
    │   └── references/
    │       ├── models.md        # Whisper モデル比較・速度・精度
    │       └── srt_format.md    # SRT/VTT 仕様・変換・後処理
    ├── noise-clean/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── denoise.py       # メインノイズ除去スクリプト
    │   │   └── requirements.txt # Python 依存パッケージ
    │   └── references/
    │       └── audio_filters.md # FFmpeg 音声フィルター詳細
    └── video-pipeline/
        ├── SKILL.md
        └── references/
            ├── tutorial_workflow.md  # チュートリアル動画向けワークフロー
            └── platform_presets.md   # YouTube/SNS 向け書き出し設定
```

## Progressive Disclosure パターン

各スキルは3層構造で情報を段階的に開示する：

1. **YAML frontmatter の description** -- スキル一覧に常に表示。エージェントがスキルをいつ使うか判断する材料
2. **SKILL.md 本文** -- スキル呼び出し時に読み込まれる。よく使うコマンドと基本手順
3. **references/** -- 必要に応じてオンデマンドで読み込まれる。詳細なリファレンス、トラブルシューティング

これにより、コンテキストウィンドウの消費を抑えつつ、必要な情報に確実にアクセスできる。

## スキル間の連携

```
video-pipeline（オーケストレーター）
  ├── noise-clean     … Step 1: ノイズ除去
  ├── ffmpeg-edit      … Step 2: 無音カット・結合
  ├── whisper-caption  … Step 3: 文字起こし・SRT 生成
  └── ffmpeg-edit      … Step 4: 字幕焼き込み・書き出し
```

`video-pipeline` はユーザーの要求に応じて各スキルを順番に呼び出す。
個別のスキルは単独でも使用可能。

## スクリプトのパス参照

SKILL.md 内でバンドルされたスクリプトを参照する際は `${CLAUDE_SKILL_DIR}` 変数を使う。
これにより、プラグインのインストール先に依存しないパスが保証される。

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/denoise.py input.mp4 output.mp4
```
