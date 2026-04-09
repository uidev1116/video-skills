# カット・分割・結合の詳細

## 無音検出結果からカット点を計算する

silencedetect の出力をパースして、カット不要な区間（発話部分）だけ抽出するスクリプト：

```python
import subprocess
import re

def get_speaking_segments(input_file, noise_db=-35, min_silence=0.8, padding=0.2):
    """
    無音区間を検出して、発話区間のリストを返す。
    padding: カット点の前後に余白を追加する秒数
    """
    cmd = [
        "ffmpeg", "-i", input_file,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stderr

    # 無音区間の開始・終了を抽出
    silence_starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", output)]
    silence_ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", output)]

    # 動画の長さを取得
    duration_match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", output)
    if not duration_match:
        raise ValueError("動画の長さを取得できませんでした")
    h, m, s = duration_match.groups()
    total_duration = int(h) * 3600 + int(m) * 60 + float(s)

    # 無音区間の逆 = 発話区間
    speaking = []
    prev_end = 0.0
    for start, end in zip(silence_starts, silence_ends):
        seg_start = max(0, prev_end - padding)
        seg_end = min(total_duration, start + padding)
        if seg_end - seg_start > 0.1:  # 0.1秒以上の区間だけ追加
            speaking.append((seg_start, seg_end))
        prev_end = end

    # 最後の発話区間
    if prev_end < total_duration:
        speaking.append((max(0, prev_end - padding), total_duration))

    return speaking


def cut_and_concat(input_file, segments, output_file):
    """
    発話区間だけを切り出して結合する。
    """
    import tempfile, os

    clips = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, (start, end) in enumerate(segments):
            clip_path = os.path.join(tmpdir, f"clip_{i:04d}.mp4")
            subprocess.run([
                "ffmpeg", "-y",
                "-i", input_file,
                "-ss", str(start),
                "-to", str(end),
                "-c", "copy",
                clip_path
            ], check=True)
            clips.append(clip_path)

        # concat
        list_path = os.path.join(tmpdir, "list.txt")
        with open(list_path, "w") as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")

        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_file
        ], check=True)


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print("無音区間を検出中...")
    segments = get_speaking_segments(input_file)
    print(f"発話区間: {len(segments)} 個")
    for s, e in segments:
        print(f"  {s:.1f}s - {e:.1f}s ({e-s:.1f}s)")

    print("カット・結合中...")
    cut_and_concat(input_file, segments, output_file)
    print(f"完了: {output_file}")
```

使い方：
```bash
python3 cut_silence.py input.mp4 output_cut.mp4
```

## 言い直し部分のカット（手動指定）

Whisper の transcript を見て「言い直し」をカットするときは、
カットする区間をファイルに書いてスクリプトを使う：

```bash
# keep_segments.txt に残す区間を書く（秒単位）
# 書式: start end
# 例:
cat > keep_segments.txt << 'EOF'
0 15.5
17.2 45.0
47.8 120.3
EOF

# python で処理
python3 -c "
import subprocess, sys

with open('keep_segments.txt') as f:
    segs = [line.split() for line in f if line.strip()]

clips = []
for i, (s, e) in enumerate(segs):
    out = f'tmp_clip_{i:04d}.mp4'
    subprocess.run(['ffmpeg','-y','-i','input.mp4','-ss',s,'-to',e,'-c','copy',out], check=True)
    clips.append(out)

with open('list.txt','w') as f:
    for c in clips:
        f.write(f\"file '{c}'\n\")

subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','list.txt','-c','copy','output.mp4'], check=True)
print('完了: output.mp4')
"
```

## よくあるエラー

| エラー | 原因 | 対処 |
|-------|------|------|
| `DTS out of order` | concat 時のタイムスタンプ不整合 | `-c copy` を外して再エンコード |
| `moov atom not found` | ファイルが壊れているか未完了 | 元ファイルを確認、再ダウンロード |
| 音がズレる | `-c copy` のキーフレーム問題 | `-c copy` を外す（速度より正確さを優先） |
