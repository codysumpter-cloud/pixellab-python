from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_edit_animation_v2():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"

    # Create simple test frames (or use existing images)
    frame1 = PIL.Image.new("RGBA", (64, 64), (100, 100, 100, 255))
    frame2 = PIL.Image.new("RGBA", (64, 64), (120, 120, 120, 255))
    frame3 = PIL.Image.new("RGBA", (64, 64), (140, 140, 140, 255))

    response = client.edit_animation_v2(
        description="add a glowing blue aura",
        frames=[
            {"image": frame1, "size": {"width": 64, "height": 64}},
            {"image": frame2, "size": {"width": 64, "height": 64}},
            {"image": frame3, "size": {"width": 64, "height": 64}},
        ],
        image_size={"width": 64, "height": 64},
        seed=42,
        no_background=False,
    )

    assert len(response.images) == 3
    assert response.usage is not None

    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "edit_animation_v2_frame0.png")


def test_edit_animation_v2_with_existing_images():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    boy_image = PIL.Image.open(images_dir / "boy64.png")

    # Use the same image as multiple frames for testing
    response = client.edit_animation_v2(
        description="add fire effect",
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
    response.images[0].pil_image().save(results_dir / "edit_animation_v2_fire.png")
