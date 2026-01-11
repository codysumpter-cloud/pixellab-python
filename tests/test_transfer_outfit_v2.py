from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_transfer_outfit_v2():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "boy64.png")

    # Create simple animation frames
    frame1 = PIL.Image.new("RGBA", (64, 64), (100, 100, 100, 255))
    frame2 = PIL.Image.new("RGBA", (64, 64), (120, 120, 120, 255))

    response = client.transfer_outfit_v2(
        reference_image={"image": reference_image, "size": {"width": 64, "height": 64}},
        frames=[
            {"image": frame1, "size": {"width": 64, "height": 64}},
            {"image": frame2, "size": {"width": 64, "height": 64}},
        ],
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=False,
    )

    assert len(response.images) == 2
    assert response.usage is not None

    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "transfer_outfit_v2_frame0.png")


def test_transfer_outfit_v2_with_chibi():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    reference_image = PIL.Image.open(images_dir / "chibi_man.png")
    boy_image = PIL.Image.open(images_dir / "boy64.png")

    response = client.transfer_outfit_v2(
        reference_image={"image": reference_image, "size": {"width": 128, "height": 128}},
        frames=[
            {"image": boy_image, "size": {"width": 64, "height": 64}},
            {"image": boy_image, "size": {"width": 64, "height": 64}},
        ],
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=False,
    )

    assert len(response.images) == 2
    assert response.usage is not None

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "transfer_outfit_v2_chibi.png")
