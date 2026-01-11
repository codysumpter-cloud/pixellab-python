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


class InterpolationV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def interpolation_v2(
    client: Any,
    start_image: Dict[str, Any],
    end_image: Dict[str, Any],
    action: str,
    image_size: Union[ImageSize, Dict[str, int]],
    seed: Optional[int] = None,
    no_background: bool = True,
) -> InterpolationV2Response:
    """Generate interpolation frames between two images.

    Args:
        client: The PixelLab client instance
        start_image: Starting image with:
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        end_image: Ending image with:
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        action: Description of the transformation (e.g., "morphing", "transforming")
        image_size: Size of the output images
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: True)

    Returns:
        InterpolationV2Response containing interpolation frames and usage information

    Raises:
        ValueError: If authentication fails or validation errors occur
        requests.exceptions.HTTPError: For other HTTP-related errors
    """
    # Process start image
    if isinstance(start_image.get("image"), PIL.Image.Image):
        start_b64 = Base64Image.from_pil_image(start_image["image"]).base64
    elif isinstance(start_image.get("image"), dict):
        start_b64 = start_image["image"].get("base64")
    else:
        start_b64 = Base64Image.from_pil_image(start_image["image"]).base64

    # Process end image
    if isinstance(end_image.get("image"), PIL.Image.Image):
        end_b64 = Base64Image.from_pil_image(end_image["image"]).base64
    elif isinstance(end_image.get("image"), dict):
        end_b64 = end_image["image"].get("base64")
    else:
        end_b64 = Base64Image.from_pil_image(end_image["image"]).base64

    request_data = {
        "start_image": {
            "image": {"base64": start_b64},
            "size": start_image["size"],
        },
        "end_image": {
            "image": {"base64": end_b64},
            "size": end_image["size"],
        },
        "action": action,
        "image_size": image_size,
        "no_background": no_background,
    }

    if seed is not None:
        request_data["seed"] = seed

    try:
        response = requests.post(
            f"{client.base_url}/v2/interpolation-v2",
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

    return InterpolationV2Response(**response.json())
