"""Utilities for converting source images into Android launcher icon assets."""

from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
from typing import Dict, Mapping, Tuple

from PIL import Image, ImageDraw, ImageOps

# Launcher icon edge lengths for each density bucket in pixels.
ANDROID_ICON_SIZES: Mapping[str, int] = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
    "play-store": 512,
}

ADAPTIVE_ICON_SIZES: Mapping[str, int] = {
    "mipmap-mdpi": 108,
    "mipmap-hdpi": 162,
    "mipmap-xhdpi": 216,
    "mipmap-xxhdpi": 324,
    "mipmap-xxxhdpi": 432,
}

_WHITE = (255, 255, 255)


def _within_tolerance(color: Tuple[int, int, int], reference: Tuple[int, int, int], tolerance: int) -> bool:
    """Return True if *color* is within *tolerance* of *reference* per channel."""

    return all(abs(channel - ref) <= tolerance for channel, ref in zip(color, reference))


def _parse_color(value: str) -> Tuple[int, int, int, int]:
    """Parse a hex color string into an RGBA tuple."""

    value = value.strip().lower()
    if value == "transparent":
        return (255, 255, 255, 0)

    if value.startswith("#"):
        value = value[1:]

    if len(value) == 6:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return (r, g, b, 255)

    if len(value) == 8:
        a = int(value[0:2], 16)
        r = int(value[2:4], 16)
        g = int(value[4:6], 16)
        b = int(value[6:8], 16)
        return (r, g, b, a)

    raise ValueError(
        "background color must be #RRGGBB, #AARRGGBB, or 'transparent'"
    )


def _edge_background_color(image: Image.Image) -> Tuple[int, int, int]:
    """Estimate the dominant edge color, assuming it represents the background."""

    width, height = image.size
    if width == 0 or height == 0:
        return _WHITE

    pixels = image.load()
    samples: Counter[Tuple[int, int, int]] = Counter()

    for x in range(width):
        samples[pixels[x, 0][:3]] += 1
        samples[pixels[x, height - 1][:3]] += 1

    for y in range(height):
        samples[pixels[0, y][:3]] += 1
        samples[pixels[width - 1, y][:3]] += 1

    if not samples:
        return _WHITE

    # Choose the most common edge color.
    return samples.most_common(1)[0][0]


def _remove_edge_background(image: Image.Image, tolerance: int) -> Image.Image:
    """Remove background connected to edges by turning it transparent."""

    rgba = image.copy()
    pixels = rgba.load()
    width, height = rgba.size

    background = _edge_background_color(rgba)
    queue = deque()
    visited = [[False for _ in range(width)] for _ in range(height)]

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))

    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if not (0 <= x < width and 0 <= y < height):
            continue

        if visited[y][x]:
            continue
        visited[y][x] = True

        r, g, b, a = pixels[x, y]
        if a != 0 and not _within_tolerance((r, g, b), background, tolerance):
            continue

        if a != 0:
            pixels[x, y] = (0, 0, 0, 0)

        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                queue.append((nx, ny))

    return rgba


def load_image(source: str | Path) -> Image.Image:
    """Load an image from disk and ensure it is in RGBA mode."""

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    with Image.open(path) as img:
        return img.convert("RGBA")


def crop_icon_from_image(image: Image.Image, *, tolerance: int = 10) -> Image.Image:
    """Return a tightly cropped version of *image* without the surrounding background.

    Background colors connected to any edge are detected (within *tolerance* per
    channel) and made fully transparent before cropping to the remaining content.
    """

    if tolerance < 0 or tolerance > 255:
        raise ValueError("tolerance must be in the range [0, 255]")

    rgba = image.convert("RGBA")
    processed = _remove_edge_background(rgba, tolerance)

    bbox = processed.getbbox()
    if bbox is None:
        return processed.copy()

    cropped = processed.crop(bbox)

    width, height = cropped.size
    if width == height:
        return cropped

    # Pad to square to keep launcher icons uniform.
    edge = max(width, height)
    if cropped.mode == "RGBA":
        background = (255, 255, 255, 0)
    elif cropped.mode == "RGB":
        background = _WHITE
    else:
        background = 0

    square = Image.new(cropped.mode, (edge, edge), background)
    offset = ((edge - width) // 2, (edge - height) // 2)
    square.paste(cropped, offset)
    return square


def _apply_round_mask(image: Image.Image) -> Image.Image:
    """Return *image* with a circular alpha mask applied."""

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0] - 1, image.size[1] - 1), fill=255)

    rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
    rounded.paste(image, mask=mask)
    return rounded


def _deduce_format(filename: str, explicit_format: str | None) -> str:
    fmt = explicit_format
    if fmt is None:
        suffix = Path(filename).suffix
        if suffix:
            fmt = suffix[1:].upper()
    if fmt is None:
        fmt = "PNG"

    if fmt in {"JPG", "JPEG"}:
        return "JPEG"
    return fmt


def _save_image(image: Image.Image, path: Path, fmt: str) -> None:
    target = image
    if fmt.upper() == "WEBP" and image.mode not in {"RGBA", "RGB"}:
        target = image.convert("RGBA")

    kwargs = {}
    if fmt.upper() == "WEBP":
        kwargs["lossless"] = True

    target.save(path, format=fmt, **kwargs)


def generate_android_icons(
    icon: Image.Image,
    output_dir: str | Path,
    *,
    filename: str = "ic_launcher.webp",
    image_format: str | None = None,
    round_filename: str | None = "ic_launcher_round.webp",
    round_format: str | None = None,
    sizes: Mapping[str, int] | None = None,
) -> Dict[str, Dict[str, Path]]:
    """Generate resized Android icons.

    Returns a mapping ``density -> {"default": Path, "round": Path}`` (the ``round``
    key is present only when ``round_filename`` is provided).
    """

    if icon.mode not in {"RGB", "RGBA"}:
        icon = icon.convert("RGBA")

    sizes = dict(sizes or ANDROID_ICON_SIZES)
    for key, value in list(sizes.items()):
        if value <= 0:
            raise ValueError(f"Icon size for {key} must be positive, got {value}")

    inferred_format = _deduce_format(filename, image_format)
    round_inferred_format: str | None = None
    if round_filename:
        round_inferred_format = _deduce_format(round_filename, round_format or image_format)

    output_paths: Dict[str, Dict[str, Path]] = {}
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    for density, edge in sizes.items():
        target_dir = base_dir / density
        target_dir.mkdir(parents=True, exist_ok=True)

        resized = ImageOps.fit(icon, (edge, edge), method=Image.Resampling.LANCZOS)
        default_path = target_dir / filename

        _save_image(resized, default_path, inferred_format)

        density_outputs: Dict[str, Path] = {"default": default_path}

        if round_filename and round_inferred_format:
            round_path = target_dir / round_filename
            round_icon = _apply_round_mask(resized)
            _save_image(round_icon, round_path, round_inferred_format)
            density_outputs["round"] = round_path

        output_paths[density] = density_outputs

    return output_paths


def generate_adaptive_icon_layers(
    icon: Image.Image,
    output_dir: str | Path,
    *,
    foreground_filename: str = "ic_launcher_foreground.webp",
    background_filename: str = "ic_launcher_background.webp",
    image_format: str | None = None,
    background_color: str = "#ffffff",
    foreground_scale: float = 0.9,
    xml_name: str = "ic_launcher.xml",
    xml_round_name: str = "ic_launcher_round.xml",
) -> Dict[str, Dict[str, Path]]:
    """Generate adaptive icon layer assets (foreground/background + XML)."""

    if not (0 < foreground_scale <= 1.0):
        raise ValueError("foreground_scale must be between 0 and 1")

    rgba_icon = icon.convert("RGBA") if icon.mode != "RGBA" else icon.copy()

    foreground_format = _deduce_format(foreground_filename, image_format)
    background_format = _deduce_format(background_filename, image_format)

    background_rgba = _parse_color(background_color)

    output_paths: Dict[str, Dict[str, Path]] = {}
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    for density, edge in ADAPTIVE_ICON_SIZES.items():
        target_dir = base_dir / density
        target_dir.mkdir(parents=True, exist_ok=True)

        bg_image = Image.new("RGBA", (edge, edge), background_rgba)
        bg_path = target_dir / background_filename
        _save_image(bg_image, bg_path, background_format)

        foreground_edge = max(1, int(edge * foreground_scale))
        scaled = ImageOps.contain(
            rgba_icon,
            (foreground_edge, foreground_edge),
            method=Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGBA", (edge, edge), (0, 0, 0, 0))
        offset = ((edge - scaled.width) // 2, (edge - scaled.height) // 2)
        canvas.paste(scaled, offset, scaled)

        fg_path = target_dir / foreground_filename
        _save_image(canvas, fg_path, foreground_format)

        output_paths[density] = {
            "background": bg_path,
            "foreground": fg_path,
        }

    xml_dir = base_dir / "mipmap-anydpi-v26"
    xml_dir.mkdir(parents=True, exist_ok=True)

    fg_resource = Path(foreground_filename).stem
    bg_resource = Path(background_filename).stem

    xml_content = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<adaptive-icon xmlns:android=\"http://schemas.android.com/apk/res/android\">\n"
        f"    <background android:drawable=\"@mipmap/{bg_resource}\"/>\n"
        f"    <foreground android:drawable=\"@mipmap/{fg_resource}\"/>\n"
        "</adaptive-icon>\n"
    )

    xml_path = xml_dir / xml_name
    xml_path.write_text(xml_content, encoding="utf-8")

    xml_outputs: Dict[str, Path] = {xml_name: xml_path}

    if xml_round_name:
        xml_round_path = xml_dir / xml_round_name
        xml_round_path.write_text(xml_content, encoding="utf-8")
        xml_outputs[xml_round_name] = xml_round_path

    output_paths["xml"] = xml_outputs

    return output_paths


def prepare_icon(source: str | Path, *, tolerance: int = 10) -> Image.Image:
    """Load and crop *source* image, returning the processed icon."""

    return crop_icon_from_image(load_image(source), tolerance=tolerance)
