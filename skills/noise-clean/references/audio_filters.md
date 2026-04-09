# FFmpeg 音声フィルター詳細

## anlmdn（適応型ノイズリダクション）

```
anlmdn=s=<strength>:p=<patch_size>:r=<research_size>:m=<max_patch_size>
```

| パラメータ | 意味 | 推奨値 |
|-----------|------|-------|
| `s` (strength) | ノイズ除去の強さ | 3〜15（大きいほど強く、副作用も大きい） |
| `p` (patch_size) | パッチサイズ（秒） | 0.001〜0.01 |
| `r` (research_size) | 探索範囲（秒） | p と同じか少し大きく |
| `m` (max_patch_size) | 最大パッチ | 通常 15〜30 |

### 環境別推奨設定

**エアコン・機器の一定ノイズ**:
```bash
-af "anlmdn=s=7:p=0.002:r=0.002:m=15"
```

**カフェ・オフィスのザワザワ**:
```bash
-af "anlmdn=s=10:p=0.005:r=0.005:m=20"
```

**強めのノイズ（外の音など）**:
```bash
-af "anlmdn=s=15:p=0.008:r=0.008:m=25"
```

## afftdn（FFT ベースノイズリダクション）

anlmdn より新しく、スペクトル解析を使うアプローチ：

```bash
ffmpeg -i input.mp4 -af "afftdn=nf=-25" output.mp4
```

`nf` はノイズフロア（dB）。-20〜-35 の範囲で調整。

## 帯域フィルター（声の周波数だけ残す）

人の声は概ね 80Hz〜8000Hz の範囲。

```bash
ffmpeg -i input.mp4 -af "highpass=f=80,lowpass=f=8000" output.mp4
```

スクリーンキャスト用途（ナレーションのみ）は帯域を絞ってもOK:
```bash
ffmpeg -i input.mp4 -af "highpass=f=200,lowpass=f=5000" output.mp4
```

## 推奨チェーン（全部組み合わせ）

```bash
ffmpeg -i input.mp4 \
  -af "highpass=f=100,anlmdn=s=7:p=0.002:r=0.002:m=15,loudnorm=I=-14:LRA=11:TP=-1" \
  output_clean.mp4
```

## 効果の確認方法

```bash
# 元音声の周波数分布を確認
ffmpeg -i input.mp4 -af "astats" -f null - 2>&1 | grep -E "RMS|Peak"

# 波形を画像で確認
ffmpeg -i input.mp4 -filter_complex "showwavespic=s=1280x200" waveform.png
```
