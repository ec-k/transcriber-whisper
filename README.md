# transcriber-whisper

音声ファイルを [faster-whisper](https://github.com/SYSTRAN/faster-whisper) で文字起こしし、
本文のみの Markdown として出力する CLI ツール。

無音のギャップ（既定 1.5 秒）を境に段落を分け、段落間は空行で区切る。

## インストール

Windows 向けには GitHub Releases に単体実行ファイル（zip）がある。展開して
`transcriber-whisper.exe` を実行すれば Python も uv も要らない。CUDA ランタイム込みで
約 2GB になる。

ソースから使う場合:

```bash
uv sync
```

ffmpeg のインストールは不要（音声デコードは PyAV 経由で行われる）。
mp3 / wav / m4a / flac などが扱える。

CUDA Toolkit のインストールも不要。GPU 実行に必要な cuBLAS 12 と cuDNN 9 は
`nvidia-cublas-cu12` / `nvidia-cudnn-cu12` として依存に含めてあり、`uv sync` で入る
（このため初回の `uv sync` は約 1.2GB をダウンロードする）。

## 使い方

```bash
uv run transcriber-whisper <input> <output.md>
```

例:

```bash
# 日本語音声（既定）
uv run transcriber-whisper meeting.mp3 meeting.md

# 英語音声を軽量モデルで
uv run transcriber-whisper sample.wav out.md --model small --language en

# 言語を自動判定
uv run transcriber-whisper unknown.m4a out.md --language auto
```

出力される Markdown:

```markdown
今日はお集まりいただきありがとうございます。まずは前回の議事録の確認から始めます。

次に、今期の売上について報告します。前年比で一二パーセントの増加となりました。
```

## オプション

| オプション | 既定値 | 説明 |
|---|---|---|
| `input` | （必須） | 入力音声ファイルのパス |
| `output` | （必須） | 出力 Markdown ファイルのパス |
| `--model` | `large-v3-turbo` | Whisper モデルサイズ。速度優先なら `small`、精度優先なら `large-v3` |
| `--language` | `ja` | 話されている言語コード。`auto` で自動判定 |

## 注記

- **初回実行時にモデルをダウンロードする。** HuggingFace のキャッシュへ保存され
  （`large-v3-turbo` で約 1.6GB）、2 回目以降はダウンロードされない。
- **GPU は自動で使われる。** NVIDIA GPU があれば `device="auto"` により GPU で動作し、
  なければ CPU にフォールバックする。
- **CUDA ランタイムは同梱している。** ctranslate2 は `cublas64_12.dll` と `cudnn64_9.dll` を
  OS のローダー経由で解決するため、`transcriber_whisper/__init__.py` が
  `site-packages/nvidia/*/bin` を DLL 検索パスへ登録してから faster-whisper を import する。
  システム側の CUDA Toolkit には依存しない。
- 既定モデルを `large-v3-turbo` にしているのは、`large-v3` が CPU では極端に遅い一方、
  turbo は日本語でも実用精度を保ったまま数倍速いため。精度が必要なときだけ `--model large-v3` を指定する。

## ビルド

`v` から始まるタグを push すると `.github/workflows/build.yml` が Nuitka で
Windows 向けの standalone バイナリを作り、Release に zip を添付する。
手元で同じものを作る場合:

```bash
uv sync
uv run --with "nuitka>=4.2" python -m nuitka --standalone \
  --output-dir=build --output-filename=transcriber-whisper.exe \
  --include-package-data=faster_whisper \
  --include-data-dir=.venv/Lib/site-packages/nvidia=nvidia \
  src/transcriber_whisper/__main__.py
```

## サードパーティライセンス

依存パッケージのライセンスは [third_party_notices.md](third_party_notices.md) にまとめてある。
依存を変更したら再生成する:

```bash
uv run --script scripts/generate_third_party_notices.py
```

`pyproject.toml` や `uv.lock` の変更を main へ push した場合は CI が再生成して自動コミットする。
