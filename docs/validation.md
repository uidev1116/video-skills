# 動作確認手順

## ファイル構成チェック

```bash
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.txt" -o -name "*.json" \) \
  | grep -v ".git" | grep -v "docs/" | sort
```

## SKILL.md フォーマットチェック

```bash
python3 -c "
from pathlib import Path

for skill_md in sorted(Path('skills').glob('*/SKILL.md')):
    content = skill_md.read_text()
    if not content.startswith('---'):
        print(f'ERROR: {skill_md} に frontmatter がありません')
        continue
    end = content.index('---', 3)
    frontmatter = content[3:end]
    if 'name:' not in frontmatter:
        print(f'ERROR: {skill_md} に name: がありません')
    if 'description:' not in frontmatter:
        print(f'ERROR: {skill_md} に description: がありません')
    else:
        print(f'OK: {skill_md}')
"
```

## 依存関係チェック

```bash
ffmpeg -version | head -1
python3 --version
pip install -r skills/noise-clean/scripts/requirements.txt
python3 -c "import noisereduce, librosa, soundfile; print('noisereduce: OK')"
pip install faster-whisper
python3 -c "from faster_whisper import WhisperModel; print('faster-whisper: OK')"
```

## 動作確認（テスト用の短い動画で）

```bash
# テスト用の 10 秒動画を生成
ffmpeg -f lavfi -i "sine=frequency=440:duration=10" \
  -f lavfi -i "color=c=blue:size=640x360:duration=10" \
  -map 1:v -map 0:a test_input.mp4

# ffmpeg-edit の基本動作
ffmpeg -i test_input.mp4 -ss 0 -to 5 -c copy test_cut.mp4
echo "ffmpeg-edit: OK"

# noise-clean の動作（FFmpeg 方式）
python3 skills/noise-clean/scripts/denoise.py test_input.mp4 test_clean.mp4 --method ffmpeg
echo "noise-clean: OK"

# クリーンアップ
rm -f test_input.mp4 test_cut.mp4 test_clean.mp4
```

## Claude Code プラグインとしてのテスト

```bash
claude --plugin-dir .
```

起動後に以下を確認：
- `/video-skills:ffmpeg-edit` でスキルが呼び出せる
- `/video-skills:whisper-caption` でスキルが呼び出せる
- `/video-skills:noise-clean` でスキルが呼び出せる
- `/video-skills:video-pipeline` でスキルが呼び出せる
