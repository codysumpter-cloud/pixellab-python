from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize

if TYPE_CHECKING:
    from .client import PixelLabClient


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


class GenerateTilesetResponse(BaseModel):
    tileset: TilesetData
    metadata: TilesetMetadata
    usage: Optional[Usage] = None


def generate_tileset(
    client: Any,
    inner_description: str,
    outer_description: str,
    tile_size: Union[ImageSize, Dict[str, int]] = None,
    transition_description: Optional[str] = None,
    transition_size: float = 0.0,
    text_guidance_scale: float = 8.0,
    outline: Optional[str] = None,
    shading: Optional[str] = None,
    detail: Optional[str] = None,
    seed: int = 0,
    polling_interval: float = 5.0,
    max_polling_time: float = 500.0,
    **kwargs
) -> GenerateTilesetResponse:
    """Generate seamless game tileset.

    Args:
        client: The PixelLab client instance
        inner_description: Description of the inner/lower terrain (e.g., 'ocean', 'grass')
        outer_description: Description of the outer/upper terrain (e.g., 'sand', 'dirt')
        tile_size: Size of individual tiles (16x16 or 32x32)
        transition_description: Description of transition area (optional)
        transition_size: Size of transition area (0.0, 0.25, 0.5, or 1.0)
        text_guidance_scale: How closely to follow the text description (1.0-20.0)
        outline: Outline style (optional)
        shading: Shading style (optional)
        detail: Detail level (optional)
        seed: Seed for deterministic generation
        polling_interval: Seconds between status checks (default: 5.0)
        max_polling_time: Maximum seconds to wait for completion (default: 300.0)
        **kwargs: Additional parameters like lower_reference_image, upper_reference_image,
                  transition_reference_image, color_image

    Returns:
        GenerateTilesetResponse containing the tileset with all tiles and metadata

    Raises:
        ValueError: If authentication fails or validation errors occur
        TimeoutError: If tileset generation exceeds max_polling_time
        requests.exceptions.HTTPError: For other HTTP-related errors
    """
    if tile_size is None:
        tile_size = {"width": 16, "height": 16}

    request_data = {
        "lower_description": inner_description,
        "upper_description": outer_description,
        "tile_size": tile_size,
        "transition_size": transition_size,
        "text_guidance_scale": text_guidance_scale,
        "seed": seed,
        **kwargs
    }

    # Add optional parameters if provided
    if transition_description:
        request_data["transition_description"] = transition_description
    if outline:
        request_data["outline"] = outline
    if shading:
        request_data["shading"] = shading
    if detail:
        request_data["detail"] = detail

    try:
        response = requests.post(
            f"{client.base_url}/v2/create-tileset",
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
    return GenerateTilesetResponse(**result)


def _poll_for_tileset(
    client: Any,
    tileset_id: str,
    background_job_id: Optional[str],
    polling_interval: float,
    max_polling_time: float,
) -> GenerateTilesetResponse:
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
                        # Extract error from last_response if available
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
                return GenerateTilesetResponse(**response.json())

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