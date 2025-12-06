from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_generate_image_v2():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_image_v2(
        description="a cute red dragon",
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=True,
    )

    assert len(response.images) == 16
    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "generate_image_v2.png")


def test_generate_image_v2_with_reference():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "boy64.png")

    response = client.generate_image_v2(
        description="a warrior with a sword",
        image_size={"width": 64, "height": 64},
        reference_images=[
            {
                "image": reference_image,
                "size": {"width": 64, "height": 64},
            }
        ],
        seed=42,
        no_background=True,
    )

    assert len(response.images) == 16
    assert response.usage is not None
