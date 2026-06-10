from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import random
from typing import Optional


Color = tuple[int, int, int]


@dataclass(frozen=True)
class SyntheticConfig:
    output_dir: Path
    image_count: int = 30
    width: int = 320
    height: int = 180
    seed: int = 7
    name: str = "synthetic_seed"


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    def to_xywh(self) -> list[int]:
        return [self.x, self.y, self.width, self.height]


class RasterCanvas:
    def __init__(self, width: int, height: int, background: Color) -> None:
        self.width = width
        self.height = height
        self.pixels = [background for _ in range(width * height)]

    def rectangle(self, x: int, y: int, width: int, height: int, color: Color) -> None:
        for row in range(max(y, 0), min(y + height, self.height)):
            for col in range(max(x, 0), min(x + width, self.width)):
                self.pixels[row * self.width + col] = color

    def circle(self, center_x: int, center_y: int, radius: int, color: Color) -> None:
        radius_squared = radius * radius
        for row in range(max(center_y - radius, 0), min(center_y + radius + 1, self.height)):
            for col in range(max(center_x - radius, 0), min(center_x + radius + 1, self.width)):
                if (col - center_x) ** 2 + (row - center_y) ** 2 <= radius_squared:
                    self.pixels[row * self.width + col] = color

    def line(self, x1: int, y1: int, x2: int, y2: int, thickness: int, color: Color) -> None:
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for step in range(steps + 1):
            t = step / steps
            x = round(x1 + (x2 - x1) * t)
            y = round(y1 + (y2 - y1) * t)
            self.rectangle(x - thickness // 2, y - thickness // 2, thickness, thickness, color)

    def noise(self, rng: random.Random, amount: int = 12) -> None:
        noisy_pixels = []
        for red, green, blue in self.pixels:
            offset = rng.randint(-amount, amount)
            noisy_pixels.append(
                (
                    _clamp(red + offset),
                    _clamp(green + offset),
                    _clamp(blue + offset),
                )
            )
        self.pixels = noisy_pixels

    def blur_blocks(self, block_size: int = 2) -> None:
        if block_size <= 1:
            return
        for y in range(0, self.height, block_size):
            for x in range(0, self.width, block_size):
                samples = []
                for row in range(y, min(y + block_size, self.height)):
                    for col in range(x, min(x + block_size, self.width)):
                        samples.append(self.pixels[row * self.width + col])
                red = sum(pixel[0] for pixel in samples) // len(samples)
                green = sum(pixel[1] for pixel in samples) // len(samples)
                blue = sum(pixel[2] for pixel in samples) // len(samples)
                for row in range(y, min(y + block_size, self.height)):
                    for col in range(x, min(x + block_size, self.width)):
                        self.pixels[row * self.width + col] = (red, green, blue)

    def write_ppm(self, path: Path) -> None:
        header = f"P6\n{self.width} {self.height}\n255\n".encode("ascii")
        body = bytes(channel for pixel in self.pixels for channel in pixel)
        path.write_bytes(header + body)


def generate_synthetic_dataset(config: SyntheticConfig) -> Path:
    rng = random.Random(config.seed)
    image_dir = config.output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    images = []
    split_ids = {"train": [], "validation": [], "test": []}
    class_cycle = [
        "handgun_visible",
        "long_gun_visible",
        "knife_visible",
        "fire_or_smoke",
        "obstacle",
        "person_close",
        None,
    ]

    for index in range(config.image_count):
        label = class_cycle[index % len(class_cycle)]
        image_id = f"synthetic_{index:05d}"
        file_name = f"data/processed/{config.name}/images/{image_id}.ppm"
        local_image_path = image_dir / f"{image_id}.ppm"

        canvas = _create_background(config.width, config.height, rng)
        annotations = []

        if label is not None:
            box = _draw_label(canvas, label, rng)
            annotations.append(
                {
                    "id": f"ann_{index:05d}_000",
                    "label": label,
                    "bbox_xywh": box.to_xywh(),
                    "annotator": "synthetic_generator",
                    "review_status": "reviewed",
                }
            )
        else:
            _draw_hard_negative(canvas, rng)

        if rng.random() < 0.45:
            _draw_occluder(canvas, rng)
        if rng.random() < 0.7:
            canvas.noise(rng, amount=rng.randint(4, 14))
        if rng.random() < 0.25:
            canvas.blur_blocks(block_size=2)

        canvas.write_ppm(local_image_path)
        images.append(
            {
                "id": image_id,
                "file_name": file_name,
                "width": config.width,
                "height": config.height,
                "annotations": annotations,
            }
        )
        split_ids[_split_for_index(index, config.image_count)].append(image_id)

    manifest = {
        "version": 1,
        "name": config.name,
        "description": "Synthetic pretraining seed generated from simple shapes and hard negatives.",
        "license": "synthetic-generated",
        "source": "scripts/generate_synthetic_dataset.py",
        "splits": split_ids,
        "images": images,
    }
    manifest_path = config.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _create_background(width: int, height: int, rng: random.Random) -> RasterCanvas:
    base = rng.choice(
        [
            (42, 50, 56),
            (92, 86, 74),
            (114, 124, 112),
            (34, 38, 45),
            (160, 154, 136),
        ]
    )
    canvas = RasterCanvas(width, height, base)
    for _ in range(rng.randint(5, 12)):
        color = tuple(_clamp(channel + rng.randint(-35, 35)) for channel in base)
        canvas.rectangle(
            rng.randint(0, width - 1),
            rng.randint(0, height - 1),
            rng.randint(12, max(14, width // 4)),
            rng.randint(8, max(10, height // 3)),
            color,
        )
    return canvas


def _draw_label(canvas: RasterCanvas, label: str, rng: random.Random) -> Box:
    width = canvas.width
    height = canvas.height
    object_width = rng.randint(max(28, width // 8), max(32, width // 3))
    object_height = rng.randint(max(18, height // 10), max(22, height // 3))
    x = rng.randint(8, max(9, width - object_width - 8))
    y = rng.randint(8, max(9, height - object_height - 8))
    box = Box(x, y, object_width, object_height)

    dark = rng.choice([(24, 24, 24), (38, 38, 42), (58, 53, 48)])
    bright = rng.choice([(190, 80, 32), (220, 135, 42), (180, 180, 170)])

    if label == "handgun_visible":
        canvas.rectangle(x, y + object_height // 3, object_width * 3 // 4, object_height // 4, dark)
        canvas.rectangle(x + object_width // 2, y + object_height // 2, object_width // 6, object_height // 2, dark)
        canvas.rectangle(x + object_width * 3 // 4, y + object_height // 3, object_width // 4, object_height // 8, dark)
    elif label == "long_gun_visible":
        canvas.rectangle(x, y + object_height // 2, object_width, max(5, object_height // 7), dark)
        canvas.rectangle(x + object_width // 6, y + object_height // 2 + 6, object_width // 5, object_height // 3, dark)
        canvas.rectangle(x + object_width * 3 // 4, y + object_height // 3, object_width // 5, object_height // 6, dark)
    elif label == "knife_visible":
        canvas.line(x, y + object_height // 2, x + object_width * 3 // 4, y + object_height // 3, max(5, object_height // 7), (190, 190, 180))
        canvas.rectangle(x + object_width * 2 // 3, y + object_height // 3, object_width // 3, object_height // 4, dark)
    elif label == "fire_or_smoke":
        for radius in range(max(object_width, object_height) // 5, 4, -5):
            canvas.circle(x + object_width // 2, y + object_height // 2, radius, bright)
        for _ in range(4):
            canvas.circle(
                x + rng.randint(0, object_width),
                y + rng.randint(0, object_height),
                rng.randint(8, max(9, object_height // 3)),
                (95, 95, 88),
            )
    elif label == "obstacle":
        canvas.rectangle(x, y, object_width, object_height, rng.choice([(88, 78, 70), (120, 98, 62), (72, 82, 92)]))
        canvas.line(x, y, x + object_width, y + object_height, 3, (35, 35, 35))
    elif label == "person_close":
        canvas.circle(x + object_width // 2, y + object_height // 5, max(8, object_width // 8), (80, 64, 54))
        canvas.rectangle(x + object_width // 3, y + object_height // 3, object_width // 3, object_height // 2, (44, 80, 128))
        canvas.line(x + object_width // 3, y + object_height // 2, x, y + object_height * 3 // 4, 4, (44, 80, 128))
        canvas.line(x + object_width * 2 // 3, y + object_height // 2, x + object_width, y + object_height * 3 // 4, 4, (44, 80, 128))

    return box


def _draw_hard_negative(canvas: RasterCanvas, rng: random.Random) -> None:
    x = rng.randint(20, max(21, canvas.width - 80))
    y = rng.randint(20, max(21, canvas.height - 70))
    color = rng.choice([(20, 70, 120), (80, 80, 84), (130, 110, 70)])
    shape = rng.choice(["phone", "flashlight", "tool", "umbrella"])
    if shape == "phone":
        canvas.rectangle(x, y, 36, 64, color)
        canvas.rectangle(x + 4, y + 4, 28, 48, (20, 20, 22))
    elif shape == "flashlight":
        canvas.rectangle(x, y + 20, 70, 14, color)
        canvas.circle(x + 70, y + 27, 14, (150, 150, 130))
    elif shape == "tool":
        canvas.line(x, y, x + 70, y + 50, 7, color)
        canvas.circle(x + 72, y + 52, 12, color)
    else:
        canvas.line(x, y + 50, x + 80, y + 5, 3, color)
        for angle in range(0, 180, 30):
            end_x = x + 40 + round(math.cos(math.radians(angle)) * 40)
            end_y = y + 45 - round(math.sin(math.radians(angle)) * 40)
            canvas.line(x + 40, y + 45, end_x, end_y, 2, color)


def _draw_occluder(canvas: RasterCanvas, rng: random.Random) -> None:
    canvas.rectangle(
        rng.randint(0, canvas.width - 1),
        rng.randint(0, canvas.height - 1),
        rng.randint(12, max(13, canvas.width // 5)),
        rng.randint(10, max(11, canvas.height // 4)),
        rng.choice([(15, 15, 15), (210, 205, 190), (70, 68, 64)]),
    )


def _split_for_index(index: int, total: int) -> str:
    fraction = index / max(total, 1)
    if fraction < 0.7:
        return "train"
    if fraction < 0.85:
        return "validation"
    return "test"


def _clamp(value: int) -> int:
    return max(0, min(255, value))
