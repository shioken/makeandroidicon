from pathlib import Path

from PIL import Image, ImageDraw

from makeandroidicon.icon_generator import (
    ANDROID_ICON_SIZES,
    crop_icon_from_image,
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
