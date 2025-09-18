"""コマンドラインインターフェース。"""

from __future__ import annotations

import argparse
from pathlib import Path

from .icon_generator import generate_android_icons, prepare_icon


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "入力画像から白い余白を取り除き、Android向けランチャーアイコンを生成します。"
        ),
    )
    parser.add_argument(
        "source",
        type=Path,
        help="白い余白が含まれる元画像へのパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build/icons"),
        help="生成した各densityフォルダを出力するディレクトリ",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=10,
        help=(
            "白背景判定の許容値 (0-255)。背景がわずかに灰色の場合は値を上げます。"
        ),
    )
    parser.add_argument(
        "--filename",
        default="ic_launcher.webp",
        help="各densityフォルダに保存するファイル名",
    )
    parser.add_argument(
        "--format",
        default=None,
        help="出力フォーマット (例: webp, png)。未指定ならファイル拡張子から推測",
    )
    parser.add_argument(
        "--round-filename",
        default="ic_launcher_round.webp",
        help="ラウンドアイコンを書き出すファイル名 (空文字で無効化)",
    )
    parser.add_argument(
        "--round-format",
        default=None,
        help="ラウンドアイコンのフォーマット。省略時は round-filename から推測",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    icon = prepare_icon(args.source, tolerance=args.tolerance)
    round_filename = args.round_filename if args.round_filename else None

    outputs = generate_android_icons(
        icon,
        args.output,
        filename=args.filename,
        image_format=args.format.upper() if args.format else None,
        round_filename=round_filename,
        round_format=args.round_format.upper() if args.round_format else None,
    )

    print("以下のアイコンを生成しました:")
    for density in sorted(outputs):
        variants = outputs[density]
        for variant, path in variants.items():
            label = density if variant == "default" else f"{density} ({variant})"
            print(f" - {label}: {path}")
