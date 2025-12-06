from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_edit_images_v2_with_text():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "boy64.png")

    edit_images = [
        {"image": reference_image, "width": 64, "height": 64}
        for _ in range(4)
    ]

    response = client.edit_images_v2(
        edit_images=edit_images,
        image_size={"width": 64, "height": 64},
        method="edit_with_text",
        description="add wings to the character",
        seed=42,
        no_background=True,
    )

    assert len(response.images) == len(edit_images)
    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "edit_images_v2_with_text.png")


def test_edit_images_v2_with_reference():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    source_image = PIL.Image.open(images_dir / "boy64.png")
    reference_image = PIL.Image.open(images_dir / "chibi_man.png")

    edit_images = [
        {"image": source_image, "width": 64, "height": 64}
        for _ in range(3)
    ]

    response = client.edit_images_v2(
        edit_images=edit_images,
        image_size={"width": 64, "height": 64},
        method="edit_with_reference",
        reference_image={
            "image": reference_image,
            "width": 128,
            "height": 128,
        },
        seed=42,
        no_background=True,
    )

    assert len(response.images) == len(edit_images)
    assert response.usage is not None
