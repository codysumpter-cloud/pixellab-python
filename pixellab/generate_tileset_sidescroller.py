from __future__ import annotations

import time
from typing import Any, Dict, List, Literal, Optional, Union

import PIL.Image
import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize
from .types import Detail, Outline, Shading


class Usage(BaseModel):
    type: Literal["usd"] = "usd"
    usd: float


class TileCorners(BaseModel):
    NW: Literal["lower", "upper", "transition"]
    NE: Literal["lower", "upper", "transition"]
    SW: Literal["lower", "upper", "transition"]
    SE: Literal["lower", "upper", "transition"]


class TileConnections(BaseModel):
    north: List[str]
    south: List[str]
    east: List[str]
    west: List[str]


class TilePattern4x4(BaseModel):
    row_0: List[int]
    row_1: List[int]
    row_2: List[int]
    row_3: List[int]


class OriginalPosition(BaseModel):
    row: int
    col: int


class Tile(BaseModel):
    id: str
    name: str
    image: Base64Image
    corners: TileCorners
    pattern_4x4: TilePattern4x4
    original_position: OriginalPosition
    description: Optional[str] = None
    connections: Optional[TileConnections] = None


class TilesetData(BaseModel):
    total_tiles: int
    tile_size: Dict[str, int]
    terrain_types: List[str]
    tiles: List[Tile]


class TilesetMetadata(BaseModel):
    edge_types: List[str]
    terrain_prompts: Dict[str, str]
    terrain_ids: Optional[Dict[str, str]] = None
    transition_size: float
    view: str
    generation_parameters: Dict[str, Any]
    created_at: str


class GenerateTilesetSidescrollerResponse(BaseModel):
    tileset: TilesetData
    metadata: TilesetMetadata
    usage: Optional[Usage] = None


def generate_tileset_sidescroller(
    client: Any,
    lower_description: str,
    transition_description: Optional[str] = None,
    tile_size: Union[ImageSize, Dict[str, int], None] = None,
    transition_size: float = 0.0,
    text_guidance_scale: float = 8.0,
    tile_strength: float = 1.0,
    tileset_adherence_freedom: float = 500.0,
    tileset_adherence: float = 100.0,
    outline: Optional[Outline] = None,
    shading: Optional[Shading] = None,
    detail: Optional[Detail] = None,
    seed: Optional[int] = None,
    lower_reference_image: Optional[PIL.Image.Image] = None,
    transition_reference_image: Optional[PIL.Image.Image] = None,
    color_image: Optional[PIL.Image.Image] = None,
    lower_base_tile_id: Optional[str] = None,
    polling_interval: float = 5.0,
    max_polling_time: float = 500.0,
) -> GenerateTilesetSidescrollerResponse:
    """Generate a sidescroller platform tileset for 2D platformer games.

    Creates platform tilesets with transparent backgrounds designed for
    side-scrolling games. The view is always "side" perspective.

    Args:
        client: The PixelLab client instance
        lower_description: Description of the main platform material
            (e.g., 'stone bricks', 'grass ground', 'metal grating')
        transition_description: Optional description of decorative layer on top
            of platform (e.g., 'moss and vines', 'snow cover', 'rust stains')
        tile_size: Size of individual tiles (16x16 or 32x32)
        transition_size: Size of transition area (0.0, 0.25, 0.5, or 1.0)
        text_guidance_scale: How closely to follow text descriptions (1.0-20.0)
        tile_strength: Strength of tile pattern adherence (0.1-2.0)
        tileset_adherence_freedom: Flexibility when following tileset structure (0.0-900.0)
        tileset_adherence: How much to follow reference/texture image (0.0-500.0)
        outline: Outline style
        shading: Shading style
        detail: Detail level
        seed: Seed for reproducible generation
        lower_reference_image: Reference image for platform terrain style
        transition_reference_image: Reference image for transition area style
        color_image: Reference image for color palette
        lower_base_tile_id: Optional ID to identify the lower base tile in metadata
        polling_interval: Seconds between status checks (default: 5.0)
        max_polling_time: Maximum seconds to wait for completion (default: 500.0)

    Returns:
        GenerateTilesetSidescrollerResponse containing the tileset with all
        tiles and metadata

    Raises:
        ValueError: If authentication fails or validation errors occur
        TimeoutError: If tileset generation exceeds max_polling_time
        requests.exceptions.HTTPError: For other HTTP-related errors

    Example:
        ```python
        import pixellab

        client = pixellab.Client(secret="YOUR_API_TOKEN")

        response = client.generate_tileset_sidescroller(
            lower_description="stone brick platform with carved details",
            transition_description="moss and small green plants",
            tile_size={"width": 16, "height": 16},
            transition_size=0.25,
        )

        # Access individual tiles
        for tile in response.tileset.tiles:
            tile.image.pil_image().save(f"tile_{tile.id}.png")
        ```
    """
    if tile_size is None:
        tile_size = {"width": 16, "height": 16}

    request_data: Dict[str, Any] = {
        "lower_description": lower_description,
        "tile_size": tile_size,
        "transition_size": transition_size,
        "text_guidance_scale": text_guidance_scale,
        "tile_strength": tile_strength,
        "tileset_adherence_freedom": tileset_adherence_freedom,
        "tileset_adherence": tileset_adherence,
    }

    if transition_description:
        request_data["transition_description"] = transition_description
    if outline:
        request_data["outline"] = outline
    if shading:
        request_data["shading"] = shading
    if detail:
        request_data["detail"] = detail
    if seed is not None:
        request_data["seed"] = seed
    if lower_base_tile_id:
        request_data["lower_base_tile_id"] = lower_base_tile_id
    if lower_reference_image is not None:
        request_data["lower_reference_image"] = Base64Image.from_pil_image(
            lower_reference_image
        ).model_dump()
    if transition_reference_image is not None:
        request_data["transition_reference_image"] = Base64Image.from_pil_image(
            transition_reference_image
        ).model_dump()
    if color_image is not None:
        request_data["color_image"] = Base64Image.from_pil_image(
            color_image
        ).model_dump()

    try:
        response = requests.post(
            f"{client.base_url}/v2/create-tileset-sidescroller",
            headers=client.headers(),
            json=request_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 401:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(error_detail)
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(error_detail)
        elif response.status_code == 429:
            error_detail = response.json().get("detail", "Rate limit exceeded")
            raise ValueError(error_detail)
        raise

    result = response.json()
    # Handle async response (202 with tileset_id and background_job_id)
    if response.status_code == 202 and "tileset_id" in result:
        tileset_id = result["tileset_id"]
        background_job_id = result.get("background_job_id")
        return _poll_for_tileset(
            client, tileset_id, background_job_id, polling_interval, max_polling_time
        )

    # Handle sync response (200 with tileset data)
    return GenerateTilesetSidescrollerResponse(**result)


def _poll_for_tileset(
    client: Any,
    tileset_id: str,
    background_job_id: Optional[str],
    polling_interval: float,
    max_polling_time: float,
) -> GenerateTilesetSidescrollerResponse:
    """Poll for tileset completion."""
    start_time = time.time()

    # First, poll the background job until it's complete
    if background_job_id:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= max_polling_time:
                raise TimeoutError(
                    f"Tileset generation timed out after {max_polling_time} seconds"
                )

            try:
                job_response = requests.get(
                    f"{client.base_url}/v2/background-jobs/{background_job_id}",
                    headers=client.headers(),
                )

                if job_response.status_code == 200:
                    job_data = job_response.json()
                    status = job_data.get("status", "")

                    if status in ("completed", "complete", "done"):
                        # Job is done, break out to fetch tileset
                        break
                    elif status in ("failed", "error"):
                        last_response = job_data.get("last_response", {})
                        error_msg = (
                            last_response.get("detail")
                            or job_data.get("error")
                            or "Unknown error"
                        )
                        raise ValueError(f"Tileset generation failed: {error_msg}")
                    # Still processing, wait and retry
                    time.sleep(polling_interval)
                    continue

                elif job_response.status_code == 404:
                    # Job not found, try fetching tileset directly
                    break

                job_response.raise_for_status()

            except requests.exceptions.HTTPError:
                # Fall through to try tileset endpoint
                break

    # Now fetch the completed tileset
    while True:
        elapsed = time.time() - start_time
        if elapsed >= max_polling_time:
            raise TimeoutError(
                f"Tileset generation timed out after {max_polling_time} seconds"
            )

        try:
            response = requests.get(
                f"{client.base_url}/v2/tilesets/{tileset_id}",
                headers=client.headers(),
            )

            if response.status_code == 200:
                return GenerateTilesetSidescrollerResponse(**response.json())

            if response.status_code == 423:
                # Still processing, wait and retry
                retry_after = response.headers.get("Retry-After")
                wait_time = float(retry_after) if retry_after else polling_interval
                time.sleep(min(wait_time, polling_interval))
                continue

            if response.status_code == 404:
                # Tileset not ready yet, wait and retry
                time.sleep(polling_interval)
                continue

            response.raise_for_status()

        except requests.exceptions.HTTPError:
            if response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error")
                raise ValueError(error_detail)
            raise

        time.sleep(polling_interval)
