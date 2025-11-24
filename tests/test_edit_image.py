from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_edit_image():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "chibi_man.png")

    response = client.edit_image(
        image=reference_image,
        image_size={"width": 128, "height": 128},
        description="make him hold a rifle, the rifle should be relative size to the soldier",
        width=128,
        height=128,
        seed=42,
        no_background=True,
        text_guidance_scale=8.0,
    )

    image = response.image.pil_image()
    assert isinstance(image, PIL.Image.Image)
    assert image.size == (128, 128)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)

    image.save(results_dir / "edit_image_chibi_man_with_rifle.png")
