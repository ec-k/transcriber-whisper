# transcriber-whisper

音声ファイルを [faster-whisper](https://github.com/SYSTRAN/faster-whisper) で文字起こしし、
本文のみの Markdown として出力する CLI ツール。

無音のギャップ（既定 1.5 秒）を境に段落を分け、段落間は空行で区切る。

## インストール

```bash
uv sync
```

ffmpeg のインストールは不要（音声デコードは PyAV 経由で行われる）。
mp3 / wav / m4a / flac などが扱える。

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
- **GPU は自動で使われる。** CUDA が利用可能な環境なら `device="auto"` により GPU で動作し、
  なければ CPU にフォールバックする。
- 既定モデルを `large-v3-turbo` にしているのは、`large-v3` が CPU では極端に遅い一方、
  turbo は日本語でも実用精度を保ったまま数倍速いため。精度が必要なときだけ `--model large-v3` を指定する。
