#!/usr/bin/env python3
"""Compose four approved artifact views into a fixed PNG design sheet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

PIL_IMPORT_ERROR = None
try:
    from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
except ImportError as exc:  # pragma: no cover - exercised by runtimes without Pillow
    PIL_IMPORT_ERROR = exc


CANVAS_SIZE = (1600, 1600)
MARGIN = 32
GAP = 24
LABEL_HEIGHT = 48
LABELS = ("FRONT", "SIDE", "3Q", "DETAIL")
ALLOWED_INPUT_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_INPUT_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_INPUT_PIXELS = 25_000_000


class CompositionError(ValueError):
    pass


def _validate_paths(inputs: tuple[Path, ...], output: Path) -> None:
    for path in inputs:
        if not path.is_file():
            raise CompositionError(f"input is not a file: {path}")
        if path.suffix.lower() not in ALLOWED_INPUT_SUFFIXES:
            raise CompositionError(f"unsupported input format: {path}")
    if output.suffix.lower() != ".png":
        raise CompositionError(f"output must use .png: {output}")
    if not output.parent.is_dir():
        raise CompositionError(f"output directory does not exist: {output.parent}")
    if output.exists():
        raise CompositionError(f"output already exists: {output}")
    resolved_output = output.resolve()
    if resolved_output in {path.resolve() for path in inputs}:
        raise CompositionError("output must not overwrite an input image")


def _save_no_clobber(sheet: Image.Image, output: Path) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output.stem}.", suffix=".png", dir=output.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
        sheet.save(temporary, format="PNG")
        output.hardlink_to(temporary)
    except FileExistsError as exc:
        raise CompositionError(f"output already exists: {output}") from exc
    except OSError as exc:
        raise CompositionError(f"cannot write output {output}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def compose(inputs: tuple[Path, ...], output: Path) -> None:
    _validate_paths(inputs, output)
    cell_width = (CANVAS_SIZE[0] - 2 * MARGIN - GAP) // 2
    cell_height = (CANVAS_SIZE[1] - 2 * MARGIN - GAP) // 2
    image_height = cell_height - LABEL_HEIGHT
    sheet = Image.new("RGB", CANVAS_SIZE, (242, 242, 240))
    draw = ImageDraw.Draw(sheet)

    for index, (path, label) in enumerate(zip(inputs, LABELS, strict=True)):
        try:
            with Image.open(path) as source:
                if source.format not in ALLOWED_INPUT_FORMATS:
                    raise CompositionError(
                        f"unsupported image content format {source.format or 'unknown'}: {path}"
                    )
                if source.width * source.height > MAX_INPUT_PIXELS:
                    raise CompositionError(
                        f"input image exceeds {MAX_INPUT_PIXELS} pixel limit: "
                        f"{path} ({source.width}x{source.height})"
                    )
                source.load()
                image = ImageOps.contain(
                    source.convert("RGBA"),
                    (cell_width, image_height),
                    Image.Resampling.LANCZOS,
                )
        except Image.DecompressionBombError as exc:
            raise CompositionError(f"input image exceeds Pillow safety limit: {path}") from exc
        except (OSError, UnidentifiedImageError) as exc:
            raise CompositionError(f"cannot read image {path}: {exc}") from exc

        column, row = index % 2, index // 2
        left = MARGIN + column * (cell_width + GAP)
        top = MARGIN + row * (cell_height + GAP)
        position = (
            left + (cell_width - image.width) // 2,
            top + (image_height - image.height) // 2,
        )
        sheet.paste(image, position, image)
        draw.rectangle(
            (left, top, left + cell_width - 1, top + cell_height - 1),
            outline=(58, 58, 58),
            width=2,
        )
        draw.line(
            (left, top + image_height, left + cell_width - 1, top + image_height),
            fill=(58, 58, 58),
            width=2,
        )
        draw.text((left + 16, top + image_height + 16), label, fill=(28, 28, 28))

    _save_no_clobber(sheet, output)


def self_test() -> None:
    import struct
    import zlib

    def close_color(actual: tuple[int, ...], expected: tuple[int, ...]) -> bool:
        return all(abs(left - right) <= 8 for left, right in zip(actual, expected))

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        specs = (
            ("front.png", (400, 800), (220, 40, 40)),
            ("side.jpg", (800, 400), (40, 180, 60)),
            ("three-quarter.webp", (600, 600), (50, 80, 220)),
            ("detail.png", (1200, 300), (230, 190, 30)),
        )
        inputs = []
        for name, size, color in specs:
            path = root / name
            Image.new("RGB", size, color).save(path)
            inputs.append(path)

        output = root / "artifact-design-sheet.png"
        compose(tuple(inputs), output)
        with Image.open(output) as sheet:
            assert sheet.format == "PNG"
            assert sheet.size == CANVAS_SIZE
            assert LABELS == ("FRONT", "SIDE", "3Q", "DETAIL")
            assert close_color(sheet.getpixel((410, 386)), specs[0][2])
            assert close_color(sheet.getpixel((1190, 386)), specs[1][2])
            assert close_color(sheet.getpixel((410, 1166)), specs[2][2])
            assert close_color(sheet.getpixel((1190, 1166)), specs[3][2])
            assert sheet.getpixel((100, 386)) != specs[0][2]
            assert sheet.getpixel((1190, 100)) != specs[1][2]
            for left, top in ((32, 32), (812, 32), (32, 812), (812, 812)):
                label = sheet.crop((left + 8, top + 712, left + 200, top + 755))
                assert any(max(pixel) < 100 for pixel in label.get_flattened_data())

        transparent = root / "transparent.png"
        transparent_image = Image.new("RGBA", (200, 200), (255, 0, 255, 0))
        ImageDraw.Draw(transparent_image).rectangle((50, 50, 150, 150), fill=(10, 20, 30, 255))
        transparent_image.save(transparent)
        transparent_output = root / "transparent-output.png"
        compose((transparent, *inputs[1:]), transparent_output)
        with Image.open(transparent_output) as sheet:
            assert sheet.getpixel((60, 40)) == (242, 242, 240)
            assert sheet.getpixel((410, 386)) == (10, 20, 30)

        disguised = root / "disguised.png"
        Image.new("RGB", (20, 20), (0, 0, 0)).save(disguised, format="GIF")
        try:
            compose((disguised, *inputs[1:]), root / "disguised-output.png")
        except CompositionError as exc:
            assert "content format GIF" in str(exc)
        else:
            raise AssertionError("disguised GIF was accepted as PNG")

        oversized = root / "oversized.png"
        oversized.write_bytes(inputs[0].read_bytes())
        png = bytearray(oversized.read_bytes())
        png[16:24] = struct.pack(">II", 6000, 5000)
        png[29:33] = struct.pack(">I", zlib.crc32(png[12:29]) & 0xFFFFFFFF)
        oversized.write_bytes(png)
        try:
            compose((oversized, *inputs[1:]), root / "oversized-output.png")
        except CompositionError as exc:
            assert "pixel limit" in str(exc)
        else:
            raise AssertionError("oversized image was accepted")

        protected = root / "protected.png"
        protected.write_bytes(b"keep")
        try:
            _save_no_clobber(Image.new("RGB", (20, 20)), protected)
        except CompositionError as exc:
            assert "output already exists" in str(exc)
        else:
            raise AssertionError("existing output was overwritten")
        assert protected.read_bytes() == b"keep"
    assert not root.exists()
    print("OK compose-design-sheet self-test")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--front", type=Path)
    parser.add_argument("--side", type=Path)
    parser.add_argument("--three-quarter", type=Path)
    parser.add_argument("--detail", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if PIL_IMPORT_ERROR is not None:
        parser.exit(2, "FAIL Pillow is required; install is not automatic\n")
    if args.self_test:
        self_test()
        return
    required = (args.front, args.side, args.three_quarter, args.detail, args.output)
    if any(path is None for path in required):
        parser.error("--front, --side, --three-quarter, --detail, and --output are required")
    try:
        compose(required[:4], required[4])
    except CompositionError as exc:
        parser.exit(2, f"FAIL {exc}\n")
    print(f"OK design sheet: {args.output}")


if __name__ == "__main__":
    main()
