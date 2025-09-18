"""既存のフォアグラウンド／バックグラウンド画像からアダプティブアイコン資産を生成するユーティリティ。"""

from __future__ import annotations

import argparse
from pathlib import Path

from makeandroidicon import ADAPTIVE_ICON_SIZES, generate_android_icons, prepare_icon


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="既存のforeground/background画像をアダプティブアイコン向けサイズに展開します。",
    )
    parser.add_argument("foreground", type=Path, help="foreground画像のパス")
    parser.add_argument("background", type=Path, help="background画像のパス")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build/adaptive_manual"),
        help="生成したレイヤーを出力するディレクトリ",
    )
    parser.add_argument(
        "--format",
        default="WEBP",
        help="出力フォーマット (例: WEBP, PNG)。既定は WEBP",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print("画像をクロップしています…")
    foreground = prepare_icon(args.foreground)
    background = prepare_icon(args.background)

    fmt = args.format.upper()
    suffix = fmt.lower()
    if suffix == "jpeg":
        suffix = "jpg"

    print("foreground レイヤーを生成…")
    fg_outputs = generate_android_icons(
        foreground,
        output_dir,
        filename=f"ic_launcher_foreground.{suffix}",
        image_format=fmt,
        round_filename=None,
        sizes=ADAPTIVE_ICON_SIZES,
    )

    print("background レイヤーを生成…")
    bg_outputs = generate_android_icons(
        background,
        output_dir,
        filename=f"ic_launcher_background.{suffix}",
        image_format=fmt,
        round_filename=None,
        sizes=ADAPTIVE_ICON_SIZES,
    )

    xml_dir = output_dir / "mipmap-anydpi-v26"
    xml_dir.mkdir(parents=True, exist_ok=True)

    xml_content = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<adaptive-icon xmlns:android=\"http://schemas.android.com/apk/res/android\">\n"
        "    <background android:drawable=\"@mipmap/ic_launcher_background\"/>\n"
        "    <foreground android:drawable=\"@mipmap/ic_launcher_foreground\"/>\n"
        "</adaptive-icon>\n"
    )

    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        path = xml_dir / name
        path.write_text(xml_content, encoding="utf-8")
        print(f"XML を生成: {path}")

    print("生成完了:")
    for density, path_map in fg_outputs.items():
        print(f" - {density} foreground: {path_map['default']}")
    for density, path_map in bg_outputs.items():
        print(f" - {density} background: {path_map['default']}")


if __name__ == "__main__":
    main()
