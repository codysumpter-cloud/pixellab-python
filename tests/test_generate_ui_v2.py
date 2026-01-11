from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_generate_ui_v2_button():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_ui_v2(
        description="medieval stone button",
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
    response.images[0].pil_image().save(results_dir / "generate_ui_v2_button.png")


def test_generate_ui_v2_panel():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_ui_v2(
        description="wooden inventory panel with gold border",
        image_size={"width": 256, "height": 256},
        seed=42,
        no_background=False,
    )

    assert len(response.images) > 0
    assert response.usage is not None

    pil_image = response.images[0].pil_image()
    assert pil_image.size == (256, 256)

    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    pil_image.save(results_dir / "generate_ui_v2_panel.png")
