from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_inpaint_v3_basic():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create a simple test image and mask
    inpaint_image = PIL.Image.new("RGBA", (64, 64), (100, 100, 100, 255))
    mask_image = PIL.Image.new("L", (64, 64), 0)  # Black = preserve

    # Make center region white (to be inpainted)
    for y in range(20, 44):
        for x in range(20, 44):
            mask_image.putpixel((x, y), 255)

    response = client.inpaint_v3(
        description="a red gem",
        inpainting_image={"image": inpaint_image, "size": {"width": 64, "height": 64}},
        mask_image={"image": mask_image, "size": {"width": 64, "height": 64}},
        seed=42,
        no_background=False,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    for image in response.images:
        pil_image = image.pil_image()
        assert isinstance(pil_image, PIL.Image.Image)
        assert pil_image.size == (64, 64)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "inpaint_v3_basic.png")


def test_inpaint_v3_with_existing_image():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    images_dir = Path("tests") / "images"
    boy_image = PIL.Image.open(images_dir / "boy64.png")

    # Create a mask that covers the top half
    mask_image = PIL.Image.new("L", (64, 64), 0)
    for y in range(32):
        for x in range(64):
            mask_image.putpixel((x, y), 255)

    response = client.inpaint_v3(
        description="a wizard hat",
        inpainting_image={"image": boy_image, "size": {"width": 64, "height": 64}},
        mask_image={"image": mask_image, "size": {"width": 64, "height": 64}},
        seed=42,
        no_background=False,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "inpaint_v3_wizard_hat.png")


def test_inpaint_v3_with_context():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create images
    inpaint_image = PIL.Image.new("RGBA", (64, 64), (100, 150, 100, 255))
    mask_image = PIL.Image.new("L", (64, 64), 255)  # All white = regenerate all
    context_image = PIL.Image.new("RGBA", (256, 256), (50, 100, 50, 255))

    response = client.inpaint_v3(
        description="a treasure chest",
        inpainting_image={"image": inpaint_image, "size": {"width": 64, "height": 64}},
        mask_image={"image": mask_image, "size": {"width": 64, "height": 64}},
        context_image={"image": context_image, "size": {"width": 256, "height": 256}},
        bounding_box={"x": 96, "y": 96, "width": 64, "height": 64},
        seed=42,
        no_background=False,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.images[0].pil_image().save(results_dir / "inpaint_v3_with_context.png")
