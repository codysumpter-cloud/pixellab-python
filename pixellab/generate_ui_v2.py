from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

import PIL.Image
import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize

if TYPE_CHECKING:
    from .client import PixelLabClient


class Usage(BaseModel):
    type: Literal["usd"] = "usd"
    usd: float


class GenerateUiV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def generate_ui_v2(
    client: Any,
    description: str,
    image_size: Union[ImageSize, Dict[str, int]],
    seed: Optional[int] = None,
    no_background: bool = True,
) -> GenerateUiV2Response:
    """Generate UI elements like buttons, panels, and icons.

    Args:
        client: The PixelLab client instance
        description: What to generate (e.g., "medieval stone button")
        image_size: Size of the generated images (32, 64, 128, or 256)
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: True)

    Returns:
        GenerateUiV2Response containing generated UI images and usage information

    Raises:
        ValueError: If authentication fails or validation errors occur
        requests.exceptions.HTTPError: For other HTTP-related errors
    """
    request_data = {
        "description": description,
        "image_size": image_size,
        "no_background": no_background,
    }

    if seed is not None:
        request_data["seed"] = seed

    try:
        response = requests.post(
            f"{client.base_url}/v2/generate-ui-v2",
            headers=client.headers(),
            json=request_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 400:
            error_detail = response.json().get("detail", "Bad request")
            raise ValueError(f"Bad request: {error_detail}")
        elif response.status_code == 401:
            error_detail = response.json().get("detail", "Unauthorized")
            raise ValueError(f"Authentication failed: {error_detail}")
        elif response.status_code == 402:
            error_detail = response.json().get("detail", "Insufficient credits")
            raise ValueError(f"Payment required: {error_detail}")
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Validation error")
            raise ValueError(f"Validation error: {error_detail}")
        elif response.status_code == 429:
            error_detail = response.json().get("detail", "Too many requests")
            raise ValueError(f"Rate limit exceeded: {error_detail}")
        raise

    return GenerateUiV2Response(**response.json())
