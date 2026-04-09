#!/usr/bin/env python3
"""
denoise.py — 動画・音声ファイルのノイズ除去スクリプト

使い方:
  python3 denoise.py input.mp4 output_clean.mp4
  python3 denoise.py input.mp4 output_clean.mp4 --method ffmpeg
  python3 denoise.py input.mp4 output_clean.mp4 --method noisereduce --noise-start 0 --noise-end 2.0
  python3 denoise.py input.mp4 output_clean.mp4 --method demucs
"""

import argparse
import subprocess
import sys
import os
import tempfile


def extract_audio(input_path: str, output_wav: str) -> None:
    """動画から音声を WAV で抽出する"""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "1",
        output_wav
    ], check=True, capture_output=True)


def merge_audio_to_video(original_video: str, clean_audio: str, output_path: str) -> None:
    """クリーン音声を元動画に合成する"""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", original_video,
        "-i", clean_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ], check=True, capture_output=True)


def denoise_ffmpeg(input_path: str, output_path: str) -> None:
    """FFmpeg フィルターでノイズ除去（追加依存なし）"""
    print("FFmpeg フィルターでノイズ除去中...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "highpass=f=100,anlmdn=s=7:p=0.002:r=0.002:m=15,loudnorm=I=-14:LRA=11:TP=-1",
        output_path
    ], check=True)
    print(f"完了: {output_path}")


def denoise_noisereduce(
    input_path: str,
    output_path: str,
    noise_start: float = 0.0,
    noise_end: float = 2.0
) -> None:
    """
    noisereduce ライブラリでノイズ除去。
    最初の noise_start〜noise_end 秒をノイズサンプルとして使う。
    """
    try:
        import noisereduce as nr
        import librosa
        import soundfile as sf
        import numpy as np
    except ImportError:
        print("ERROR: 必要なライブラリが未インストールです。")
        print("実行してください: pip install noisereduce librosa soundfile")
        sys.exit(1)

    print("音声を抽出中...")
    is_video = not input_path.lower().endswith((".wav", ".mp3", ".flac"))

    with tempfile.TemporaryDirectory() as tmpdir:
        if is_video:
            audio_path = os.path.join(tmpdir, "audio.wav")
            extract_audio(input_path, audio_path)
        else:
            audio_path = input_path

        print("音声を読み込み中...")
        y, sr = librosa.load(audio_path, sr=None, mono=True)

        # ノイズサンプルを取得（最初の数秒）
        noise_start_idx = int(noise_start * sr)
        noise_end_idx = int(noise_end * sr)

        if noise_end_idx > len(y):
            print(f"WARNING: 指定したノイズサンプル区間が音声より長いです。先頭1秒を使います。")
            noise_end_idx = min(int(1.0 * sr), len(y))

        noise_sample = y[noise_start_idx:noise_end_idx]

        if len(noise_sample) == 0:
            print("WARNING: ノイズサンプルが取得できませんでした。ノイズプロファイルなしで処理します。")
            noise_sample = None

        print("ノイズ除去中... (数十秒かかることがあります)")
        if noise_sample is not None:
            y_clean = nr.reduce_noise(
                y=y,
                sr=sr,
                y_noise=noise_sample,
                stationary=False,
                prop_decrease=0.85
            )
        else:
            y_clean = nr.reduce_noise(y=y, sr=sr, stationary=True)

        clean_wav = os.path.join(tmpdir, "clean.wav")
        sf.write(clean_wav, y_clean, sr)
        print("音声を書き出し中...")

        if is_video:
            merge_audio_to_video(input_path, clean_wav, output_path)
        else:
            import shutil
            shutil.copy(clean_wav, output_path)

    print(f"完了: {output_path}")


def denoise_demucs(input_path: str, output_path: str) -> None:
    """
    Demucs で音声分離（vocals だけ抽出）。
    他人の声・BGMが混入している場合に使う。
    """
    try:
        import subprocess
        subprocess.run(["demucs", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Demucs が未インストールです。")
        print("実行してください: pip install demucs")
        sys.exit(1)

    is_video = not input_path.lower().endswith((".wav", ".mp3", ".flac"))

    with tempfile.TemporaryDirectory() as tmpdir:
        if is_video:
            audio_path = os.path.join(tmpdir, "audio.wav")
            extract_audio(input_path, audio_path)
        else:
            audio_path = input_path

        print("Demucs で音声分離中... (初回は数GBのモデルをダウンロードします)")
        demucs_out = os.path.join(tmpdir, "demucs_out")
        subprocess.run([
            "demucs",
            "--two-stems=vocals",
            "-o", demucs_out,
            audio_path
        ], check=True)

        # Demucs の出力ファイルを探す
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocals_path = os.path.join(demucs_out, "htdemucs", audio_name, "vocals.wav")

        if not os.path.exists(vocals_path):
            # ファイルを探す
            for root, dirs, files in os.walk(demucs_out):
                for f in files:
                    if "vocals" in f:
                        vocals_path = os.path.join(root, f)
                        break

        if not os.path.exists(vocals_path):
            print(f"ERROR: Demucs の出力ファイルが見つかりません: {demucs_out}")
            sys.exit(1)

        print("音声を合成中...")
        if is_video:
            merge_audio_to_video(input_path, vocals_path, output_path)
        else:
            import shutil
            shutil.copy(vocals_path, output_path)

    print(f"完了: {output_path}")
    print("TIP: Demucs は音楽分離向けのため、他人の声が完全には除去されない場合があります。")
    print("     さらに除去したい場合は --method noisereduce を追加で試してください。")


def main():
    parser = argparse.ArgumentParser(description="動画・音声ファイルのノイズ除去")
    parser.add_argument("input", help="入力ファイル（.mp4, .mov, .wav など）")
    parser.add_argument("output", help="出力ファイル")
    parser.add_argument(
        "--method",
        choices=["ffmpeg", "noisereduce", "demucs"],
        default="noisereduce",
        help="ノイズ除去の手法（default: noisereduce）"
    )
    parser.add_argument(
        "--noise-start",
        type=float,
        default=0.0,
        help="ノイズサンプル開始時刻（秒）（noisereduce 用）"
    )
    parser.add_argument(
        "--noise-end",
        type=float,
        default=2.0,
        help="ノイズサンプル終了時刻（秒）（noisereduce 用）"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: 入力ファイルが見つかりません: {args.input}")
        sys.exit(1)

    print(f"入力: {args.input}")
    print(f"出力: {args.output}")
    print(f"手法: {args.method}")

    if args.method == "ffmpeg":
        denoise_ffmpeg(args.input, args.output)
    elif args.method == "noisereduce":
        denoise_noisereduce(args.input, args.output, args.noise_start, args.noise_end)
    elif args.method == "demucs":
        denoise_demucs(args.input, args.output)


if __name__ == "__main__":
    main()
