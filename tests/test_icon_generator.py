from pathlib import Path

from PIL import Image, ImageDraw

from makeandroidicon.icon_generator import (
    ADAPTIVE_ICON_SIZES,
    ANDROID_ICON_SIZES,
    crop_icon_from_image,
    generate_adaptive_icon_layers,
    generate_android_icons,
)


def test_crop_icon_from_image_trims_white_margin() -> None:
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 79, 79), fill=(0, 128, 0, 255))

    cropped = crop_icon_from_image(image, tolerance=0)

    assert cropped.size == (60, 60)
    assert cropped.getpixel((0, 0)) == (0, 128, 0, 255)


def test_crop_icon_from_image_makes_edge_background_transparent() -> None:
    image = Image.new("RGBA", (120, 120), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, 99, 99), radius=20, fill=(0, 80, 120, 255))
    draw.ellipse((50, 50, 70, 70), fill=(255, 255, 255, 255))

    cropped = crop_icon_from_image(image, tolerance=10)

    assert cropped.size[0] == cropped.size[1]
    assert cropped.getpixel((0, 0))[3] == 0
    opaque_pixels = [
        cropped.getpixel((x, y))
        for x in range(cropped.width)
        for y in range(cropped.height)
        if cropped.getpixel((x, y))[3] == 255
    ]
    assert any(pixel[:3] == (255, 255, 255) for pixel in opaque_pixels)


def test_generate_android_icons_default_webp(tmp_path: Path) -> None:
    icon = Image.new("RGBA", (256, 256), (0, 128, 0, 255))

    outputs = generate_android_icons(
        icon,
        tmp_path,
        filename="ic_launcher.png",
        image_format="PNG",
        round_filename=None,
    )

    assert set(outputs) == set(ANDROID_ICON_SIZES)

    for density, expected_size in ANDROID_ICON_SIZES.items():
        output_path = outputs[density]["default"]
        assert output_path.exists()
        assert output_path.suffix == ".png"

        with Image.open(output_path) as generated:
            assert generated.format == "PNG"
            assert generated.size == (expected_size, expected_size)


def test_generate_android_icons_webp(tmp_path: Path) -> None:
    icon = Image.new("RGBA", (256, 256), (0, 128, 0, 255))

    outputs = generate_android_icons(
        icon,
        tmp_path,
        filename="ic_launcher.webp",
        image_format="WEBP",
        round_filename="ic_launcher_round.webp",
        round_format="WEBP",
    )

    for density, expected_size in ANDROID_ICON_SIZES.items():
        default_path = outputs[density]["default"]
        round_path = outputs[density]["round"]

        with Image.open(default_path) as generated:
            assert generated.format == "WEBP"
            assert generated.size == (expected_size, expected_size)

        with Image.open(round_path) as generated_round:
            assert generated_round.format == "WEBP"
            assert generated_round.size == (expected_size, expected_size)

            # 角が透明になっていることを確認（円形マスク適用）
            assert generated_round.mode == "RGBA"
            assert generated_round.getpixel((0, 0))[3] == 0


def test_generate_adaptive_icon_layers(tmp_path: Path) -> None:
    icon = Image.new("RGBA", (512, 512), (0, 180, 255, 255))

    outputs = generate_adaptive_icon_layers(
        icon,
        tmp_path,
        foreground_filename="ic_launcher_foreground.webp",
        background_filename="ic_launcher_background.webp",
        image_format="WEBP",
        background_color="#FF0000",
        foreground_scale=0.8,
        xml_name="ic_launcher.xml",
        xml_round_name="ic_launcher_round.xml",
    )

    for density, expected_size in ADAPTIVE_ICON_SIZES.items():
        layer = outputs[density]
        foreground = layer["foreground"]
        background = layer["background"]

        with Image.open(foreground) as fg_img:
            assert fg_img.size == (expected_size, expected_size)
            assert fg_img.format == "WEBP"
            # 前景は背景より小さい
            assert fg_img.getpixel((0, 0))[3] == 0

        with Image.open(background) as bg_img:
            assert bg_img.size == (expected_size, expected_size)
            assert bg_img.format == "WEBP"
            assert bg_img.getpixel((0, 0))[:3] == (255, 0, 0)

    xml_outputs = outputs["xml"]
    xml_path = xml_outputs["ic_launcher.xml"]
    xml_round_path = xml_outputs["ic_launcher_round.xml"]

    content = xml_path.read_text(encoding="utf-8")
    assert "<adaptive-icon" in content
    assert "@mipmap/ic_launcher_foreground" in content
    assert "@mipmap/ic_launcher_background" in content
    assert xml_round_path.read_text(encoding="utf-8") == content
