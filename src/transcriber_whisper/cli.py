"""Transcribe an audio file into a plain Markdown document."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

from faster_whisper import WhisperModel

PARAGRAPH_GAP_SEC = 1.5  # this gap starts a new paragraph
NO_SPACE_LANGUAGES = {"ja", "zh", "yue", "th"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcriber-whisper",
        description="Transcribe an audio file with faster-whisper and write it as Markdown.",
    )
    parser.add_argument("input", type=Path, help="path to the audio file (mp3, wav, m4a, flac, ...)")
    parser.add_argument("output", type=Path, help="path of the Markdown file to write")
    parser.add_argument(
        "--model",
        default="large-v3-turbo",
        help="whisper model size (default: %(default)s). Use 'small' for speed or 'large-v3' for accuracy.",
    )
    parser.add_argument(
        "--language",
        default="ja",
        help="spoken language code (default: %(default)s). Pass 'auto' to detect it automatically.",
    )
    return parser


def to_paragraphs(segments: Iterable, language: str | None) -> list[str]:
    """Group segments into paragraphs, splitting on silent gaps."""
    joiner = "" if language in NO_SPACE_LANGUAGES else " "
    paragraphs: list[str] = []
    current: list[str] = []
    prev_end: float | None = None

    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if prev_end is not None and seg.start - prev_end >= PARAGRAPH_GAP_SEC and current:
            paragraphs.append(joiner.join(current))
            current = []
        current.append(text)
        prev_end = seg.end

    if current:
        paragraphs.append(joiner.join(current))
    return paragraphs


def main() -> int:
    args = build_parser().parse_args()

    if not args.input.is_file():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1

    language = None if args.language == "auto" else args.language

    print(
        f"loading model '{args.model}' (the first run downloads it from HuggingFace Hub)...",
        file=sys.stderr,
    )
    model = WhisperModel(args.model, device="auto", compute_type="default")

    segments, info = model.transcribe(
        str(args.input),
        language=language,
        vad_filter=True,
        log_progress=True,
    )

    paragraphs = to_paragraphs(segments, info.language)
    if not paragraphs:
        print("error: no speech was detected in the input file", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8", newline="\n")

    print(
        f"done: {args.output} (language={info.language}, duration={info.duration:.1f}s)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
