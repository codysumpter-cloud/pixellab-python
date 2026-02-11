from __future__ import annotations

from pathlib import Path

import PIL.Image

import pixellab


def test_generate_tileset_sidescroller_basic():
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset_sidescroller(
        lower_description="stone brick platform with carved details",
        transition_description="moss and small green plants",
        tile_size={"width": 16, "height": 16},
        transition_size=0.25,
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1
    assert len(response.tileset.tiles) >= 1

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_basic.png"
    )


def test_generate_tileset_sidescroller_minimal():
    """Test with minimal parameters - only lower_description required."""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset_sidescroller(
        lower_description="green grass ground with dirt",
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_minimal.png"
    )


def test_generate_tileset_sidescroller_styled():
    """Test with outline, shading, and detail options."""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset_sidescroller(
        lower_description="rusty metal grating platform",
        transition_description="rust stains and corrosion",
        tile_size={"width": 32, "height": 32},
        transition_size=0.5,
        outline="single color outline",
        shading="medium shading",
        detail="highly detailed",
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1

    # Check tile sizes
    for tile in response.tileset.tiles:
        assert tile.id is not None
        assert tile.image is not None
        img = tile.image.pil_image()
        assert img.size == (32, 32)

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_styled.png"
    )


def test_generate_tileset_sidescroller_seamless():
    """Test seamless sidescroller tileset generation with seed."""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    response = client.generate_tileset_sidescroller(
        lower_description="ice crystal platform with frozen surface",
        transition_description="frost and snowflakes",
        tile_size={"width": 16, "height": 16},
        transition_size=0.25,
        text_guidance_scale=12.0,
        seed=42,
    )

    # Check response
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_seamless.png"
    )


def test_generate_tileset_sidescroller_with_reference_32x32():
    """Test sidescroller tileset with 32x32 reference images for lower/transition terrain."""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create a simple 32x32 stone reference for lower terrain
    lower_ref = PIL.Image.new("RGBA", (32, 32))
    for y in range(32):
        for x in range(32):
            lower_ref.putpixel(
                (x, y), (120 + (x % 3) * 10, 120 + (y % 3) * 10, 120, 255)
            )

    # Create a simple 32x32 moss reference for transition terrain
    transition_ref = PIL.Image.new("RGBA", (32, 32))
    for y in range(32):
        for x in range(32):
            transition_ref.putpixel(
                (x, y), (34 + (x % 3) * 10, 139 + (y % 3) * 10, 34, 255)
            )

    response = client.generate_tileset_sidescroller(
        lower_description="stone brick platform",
        transition_description="moss and vines",
        tile_size={"width": 32, "height": 32},
        transition_size=0.25,
        text_guidance_scale=8.0,
        seed=42,
        lower_reference_image=lower_ref,
        transition_reference_image=transition_ref,
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1
    assert len(response.tileset.tiles) >= 1

    # Check tile sizes
    for tile in response.tileset.tiles:
        assert tile.id is not None
        assert tile.image is not None
        img = tile.image.pil_image()
        assert img.size == (32, 32)

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_with_reference_32x32.png"
    )


def test_generate_tileset_sidescroller_with_reference_16x16():
    """Test sidescroller tileset with 16x16 reference images for lower/transition terrain."""
    client = pixellab.Client.from_env_file(".env.development.secrets")

    # Create a simple 16x16 stone reference for lower terrain
    lower_ref = PIL.Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            lower_ref.putpixel(
                (x, y), (120 + (x % 3) * 10, 120 + (y % 3) * 10, 120, 255)
            )

    # Create a simple 16x16 moss reference for transition terrain
    transition_ref = PIL.Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            transition_ref.putpixel(
                (x, y), (34 + (x % 3) * 10, 139 + (y % 3) * 10, 34, 255)
            )

    response = client.generate_tileset_sidescroller(
        lower_description="stone brick platform",
        transition_description="moss and vines",
        tile_size={"width": 16, "height": 16},
        transition_size=0.25,
        text_guidance_scale=8.0,
        seed=42,
        lower_reference_image=lower_ref,
        transition_reference_image=transition_ref,
    )

    # Check response structure
    assert hasattr(response, "tileset")
    assert hasattr(response, "metadata")
    assert response.tileset.total_tiles >= 1
    assert len(response.tileset.tiles) >= 1

    # Check tile sizes
    for tile in response.tileset.tiles:
        assert tile.id is not None
        assert tile.image is not None
        img = tile.image.pil_image()
        assert img.size == (16, 16)

    # Save first tile as result
    results_dir = Path("tests") / "results"
    results_dir.mkdir(exist_ok=True)
    response.tileset.tiles[0].image.pil_image().save(
        results_dir / "tileset_sidescroller_with_reference_16x16.png"
    )
