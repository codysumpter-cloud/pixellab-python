from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_interpolation_v2():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create simple start and end images
    start_image = PIL.Image.new("RGBA", (64, 64), (255, 0, 0, 255))  # Red
    end_image = PIL.Image.new("RGBA", (64, 64), (0, 0, 255, 255))  # Blue

    response = client.interpolation_v2(
        start_image={"image": start_image, "size": {"width": 64, "height": 64}},
        end_image={"image": end_image, "size": {"width": 64, "height": 64}},
        action="morphing",
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=True,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "interpolation_v2_frame0.png")


def test_interpolation_v2_with_existing_images():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    boy_image = PIL.Image.open(images_dir / "boy64.png")
    chibi_image = PIL.Image.open(images_dir / "chibi_man.png")

    response = client.interpolation_v2(
        start_image={"image": boy_image, "size": {"width": 64, "height": 64}},
        end_image={"image": chibi_image, "size": {"width": 128, "height": 128}},
        action="transforming",
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=True,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "interpolation_v2_transform.png")
