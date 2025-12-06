from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Union, Dict, List

import PIL.Image
import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize

if TYPE_CHECKING:
    from .client import PixelLabClient


class Usage(BaseModel):
    type: Literal["usd"] = "usd"
    usd: float


class StyleImageItem(BaseModel):
    image: Base64Image
    width: int
    height: int


class GenerateWithStyleV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def generate_with_style_v2(
    client: Any,
    style_images: Union[List[StyleImageItem], List[Dict[str, Any]]],
    description: str,
    image_size: Union[ImageSize, Dict[str, int]],
    style_description: Optional[str] = None,
    seed: Optional[int] = None,
    no_background: bool = True,
) -> GenerateWithStyleV2Response:
    """Generate new images matching the style of reference images.

    Args:
        client: The PixelLab client instance
        style_images: 1-4 style reference images
        description: What to generate (1-2000 chars)
        image_size: Size of the generated images (width and height must be equal: 32, 64, 128, or 256)
        style_description: Describe the style (max 500 chars)
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: True)

    Returns:
        GenerateWithStyleV2Response containing multiple generated images and usage information

    Raises:
        ValueError: If authentication fails, validation errors occur, or constraints are violated
        requests.exceptions.HTTPError: For other HTTP-related errors

    Notes:
        - Image size must be square (32x32, 64x64, 128x128, or 256x256)
        - Output counts by size:
          - 32x32 → 64 images (8×8 grid)
          - 64x64 → 16 images (4×4 grid)
          - 128x128 → 4 images (2×2 grid)
          - 256x256 → 1 image
        - 1-4 style images can be provided
        - The endpoint consumes ~$0.18 worth of credits
    """
    # Process style_images
    processed_style_images = []
    for img in style_images:
        if isinstance(img, StyleImageItem):
            processed_style_images.append(
                {
                    "image": {"base64": img.image.base64},
                    "width": img.width,
                    "height": img.height,
                }
            )
        else:
            img_b64 = Base64Image.from_pil_image(img["image"]).base64
            processed_style_images.append(
                {
                    "image": {"base64": img_b64},
                    "width": img["width"],
                    "height": img["height"],
                }
            )

    request_data = {
        "style_images": processed_style_images,
        "description": description,
        "image_size": image_size,
        "no_background": no_background,
    }

    # Add optional parameters if provided
    if seed is not None:
        request_data["seed"] = seed

    if style_description:
        request_data["style_description"] = style_description

    try:
        response = requests.post(
            f"{client.base_url}/v2/generate-with-style-v2",
            headers=client.headers(),
            json=request_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
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

    return GenerateWithStyleV2Response(**response.json())

