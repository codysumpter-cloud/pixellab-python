from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_generate_8_rotations_v2_rotate_character():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "boy64.png")

    response = client.generate_8_rotations_v2(
        image_size={"width": 64, "height": 64},
        method="rotate_character",
        reference_image={
            "image": reference_image,
            "width": 64,
            "height": 64,
        },
        seed=42,
        no_background=True,
    )

    assert len(response.images) == 8
    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(
        results_dir / "generate_8_rotations_v2.png"
    )


def test_generate_8_rotations_v2_create_from_concept():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    concept_image = PIL.Image.open(images_dir / "chibi_man.png")

    response = client.generate_8_rotations_v2(
        image_size={"width": 64, "height": 64},
        method="create_from_concept",
        concept_image={
            "image": concept_image,
            "width": 128,
            "height": 128,
        },
        description="a pixel art warrior",
        seed=42,
        no_background=True,
    )

    assert len(response.images) == 8
    assert response.usage is not None


def test_generate_8_rotations_v2_create_with_style():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "boy64.png")

    response = client.generate_8_rotations_v2(
        image_size={"width": 64, "height": 64},
        method="create_with_style",
        reference_image={
            "image": reference_image,
            "width": 64,
            "height": 64,
        },
        description="a pixel art character",
        seed=42,
        no_background=True,
    )

    assert len(response.images) == 8
    assert response.usage is not None
