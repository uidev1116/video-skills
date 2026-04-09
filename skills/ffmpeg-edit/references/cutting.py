#!/usr/bin/env python3
"""
cutting.py — 無音区間を検出して発話部分だけを切り出し・結合するスクリプト

使い方:
  python3 cutting.py input.mp4 output_cut.mp4
  python3 cutting.py input.mp4 output_cut.mp4 --noise-db -30 --min-silence 0.5
  python3 cutting.py input.mp4 output_cut.mp4 --fast-copy   # キーフレーム精度（高速）
"""

import argparse
import subprocess
import re
import sys
import tempfile
import os


def get_speaking_segments(input_file, noise_db=-35, min_silence=0.8, padding=0.15):
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


def cut_and_concat(input_file, segments, output_file, fast_copy=False):
    """
    発話区間だけを切り出して結合する。

    fast_copy=True:  -c copy（高速だがキーフレーム精度、音飛びの可能性あり）
    fast_copy=False: 再エンコード（正確だが遅い、デフォルト）
    """
    clips = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, (start, end) in enumerate(segments):
            clip_path = os.path.join(tmpdir, f"clip_{i:04d}.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", input_file,
                "-ss", str(start),
                "-to", str(end),
            ]
            if fast_copy:
                cmd += ["-c", "copy"]
            clip_path_out = clip_path
            cmd.append(clip_path_out)
            subprocess.run(cmd, check=True, capture_output=True)
            clips.append(clip_path_out)

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
        ], check=True, capture_output=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="無音区間を検出して発話部分だけを切り出し・結合する")
    parser.add_argument("input", help="入力ファイル")
    parser.add_argument("output", help="出力ファイル")
    parser.add_argument("--noise-db", type=int, default=-35, help="無音判定の閾値 dB（default: -35）")
    parser.add_argument("--min-silence", type=float, default=0.8, help="最短無音長（秒）（default: 0.8）")
    parser.add_argument(
        "--fast-copy", action="store_true",
        help="-c copy で高速カット（キーフレーム精度、音飛びの可能性あり）"
    )
    args = parser.parse_args()

    print("無音区間を検出中...")
    segments = get_speaking_segments(args.input, noise_db=args.noise_db, min_silence=args.min_silence)
    print(f"発話区間: {len(segments)} 個")
    for s, e in segments:
        print(f"  {s:.1f}s - {e:.1f}s ({e-s:.1f}s)")

    if not args.fast_copy:
        print("カット・結合中（再エンコード、正確だが遅い）...")
    else:
        print("カット・結合中（-c copy、高速だがキーフレーム精度）...")
    cut_and_concat(args.input, segments, args.output, fast_copy=args.fast_copy)
    print(f"完了: {args.output}")
