from __future__ import annotations

from pathlib import Path

import PIL.Image
import pytest

import pixellab


def test_generate_tileset_basic():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset(
        inner_description="grass field",
        outer_description="forest",
        tile_size={"width": 16, "height": 16},
        transition_description="edge between grass and trees",
        transition_size=0.0,
        text_guidance_scale=8.0,
        view="high top-down",
        seed=0,
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16
    assert len(response.tileset.tiles) >= 16

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(results_dir / "tileset_basic.png")


def test_generate_tileset_with_style():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset(
        inner_description="water",
        outer_description="sand beach",
        tile_size={"width": 16, "height": 16},
        transition_description="waves and foam",
        transition_size=0.25,
        text_guidance_scale=10.0,
        outline="single color outline",
        shading="flat shading",
        detail="medium detail",
        view="low top-down",
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(results_dir / "tileset_styled.png")


def test_generate_tileset_minimal():
    """Test with minimal parameters"""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset(
        inner_description="stone floor",
        outer_description="dirt path",
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(results_dir / "tileset_minimal.png")


def test_generate_tileset_seamless():
    """Test seamless tileset generation"""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset(
        inner_description="lava",
        outer_description="volcanic rock",
        tile_size={"width": 16, "height": 16},
        transition_description="cooling lava and cracks",
        transition_size=0.25,
        text_guidance_scale=12.0,
        seed=42,
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(results_dir / "tileset_seamless.png")


def test_generate_tileset_with_reference_32x32():
    """Test tileset generation with 32x32 reference images for lower/upper terrain."""
    from pixellab.models import Base64Image

    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create a simple 32x32 grass reference for lower terrain
    lower_ref = PIL.Image.new("RGBA", (32, 32))
    for y in range(32):
        for x in range(32):
            lower_ref.putpixel((x, y), (34 + (x % 3) * 10, 139 + (y % 3) * 10, 34, 255))

    # Create a simple 32x32 dirt reference for upper terrain
    upper_ref = PIL.Image.new("RGBA", (32, 32))
    for y in range(32):
        for x in range(32):
            upper_ref.putpixel((x, y), (139 + (x % 3) * 10, 90 + (y % 3) * 5, 43, 255))

    lower_ref_b64 = Base64Image.from_pil_image(lower_ref)
    upper_ref_b64 = Base64Image.from_pil_image(upper_ref)

    response = client.generate_tileset(
        inner_description="grass field",
        outer_description="dirt path",
        tile_size={"width": 32, "height": 32},
        text_guidance_scale=8.0,
        seed=42,
        lower_reference_image=lower_ref_b64.model_dump(),
        upper_reference_image=upper_ref_b64.model_dump(),
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16
    assert len(response.tileset.tiles) >= 16

    # Check individual tiles
    for tile in response.tileset.tiles:
        assert tile.id is not None
        assert tile.image is not None
        img = tile.image.pil_image()
        assert img.size == (32, 32)

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_with_reference_32x32.png"
    )


def test_generate_tileset_with_reference_16x16():
    """Test tileset generation with 16x16 reference images for lower/upper terrain."""
    from pixellab.models import Base64Image

    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create a simple 16x16 grass reference for lower terrain
    lower_ref = PIL.Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            lower_ref.putpixel((x, y), (34 + (x % 3) * 10, 139 + (y % 3) * 10, 34, 255))

    # Create a simple 16x16 dirt reference for upper terrain
    upper_ref = PIL.Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            upper_ref.putpixel((x, y), (139 + (x % 3) * 10, 90 + (y % 3) * 5, 43, 255))

    lower_ref_b64 = Base64Image.from_pil_image(lower_ref)
    upper_ref_b64 = Base64Image.from_pil_image(upper_ref)

    response = client.generate_tileset(
        inner_description="grass field",
        outer_description="dirt path",
        tile_size={"width": 16, "height": 16},
        text_guidance_scale=8.0,
        seed=42,
        lower_reference_image=lower_ref_b64.model_dump(),
        upper_reference_image=upper_ref_b64.model_dump(),
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 16
    assert len(response.tileset.tiles) >= 16

    # Check individual tiles
    for tile in response.tileset.tiles:
        assert tile.id is not None
        assert tile.image is not None
        img = tile.image.pil_image()
        assert img.size == (16, 16)

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_with_reference_16x16.png"
    )