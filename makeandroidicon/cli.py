"""コマンドラインインターフェース。"""

from __future__ import annotations

import argparse
from pathlib import Path

from .icon_generator import (
    generate_adaptive_icon_layers,
    generate_android_icons,
    prepare_icon,
)


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
    parser.add_argument(
        "--adaptive",
        action="store_true",
        help="アダプティブアイコン用のレイヤー (foreground/background/XML) も生成",
    )
    parser.add_argument(
        "--adaptive-foreground",
        default="ic_launcher_foreground.webp",
        help="アダプティブアイコンのforegroundファイル名",
    )
    parser.add_argument(
        "--adaptive-background",
        default="ic_launcher_background.webp",
        help="アダプティブアイコンのbackgroundファイル名",
    )
    parser.add_argument(
        "--adaptive-format",
        default=None,
        help="アダプティブアイコンレイヤーのフォーマット (例: webp)",
    )
    parser.add_argument(
        "--adaptive-color",
        default="#ffffff",
        help="backgroundレイヤーに使うカラー (#RRGGBB / #AARRGGBB / transparent)",
    )
    parser.add_argument(
        "--adaptive-scale",
        type=float,
        default=0.9,
        help="foregroundの縮尺 (0-1)。1で背景と同じサイズ",
    )
    parser.add_argument(
        "--adaptive-xml",
        default="ic_launcher.xml",
        help="生成するアダプティブアイコンXML名",
    )
    parser.add_argument(
        "--adaptive-xml-round",
        default="ic_launcher_round.xml",
        help="ラウンド版XML名 (空文字で生成しない)",
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

    if args.adaptive:
        xml_round_name = args.adaptive_xml_round if args.adaptive_xml_round else None
        adaptive_outputs = generate_adaptive_icon_layers(
            icon,
            args.output,
            foreground_filename=args.adaptive_foreground,
            background_filename=args.adaptive_background,
            image_format=args.adaptive_format.upper() if args.adaptive_format else None,
            background_color=args.adaptive_color,
            foreground_scale=args.adaptive_scale,
            xml_name=args.adaptive_xml,
            xml_round_name=xml_round_name,
        )

        print("アダプティブアイコン用レイヤー:")
        for key in sorted(adaptive_outputs):
            variants = adaptive_outputs[key]
            if isinstance(variants, dict):
                for variant, path in variants.items():
                    label = key if key != "xml" else variant
                    if key != "xml" and variant not in {"foreground", "background"}:
                        label = f"{key} ({variant})"
                    elif key != "xml":
                        label = f"{key} ({variant})"
                    print(f" - {label}: {path}")
            else:
                print(f" - {key}: {variants}")
