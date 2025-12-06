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


class ReferenceImageItem(BaseModel):
    image: Base64Image
    size: ImageSize
    usage_description: Optional[str] = None


class StyleImageItem(BaseModel):
    image: Base64Image
    size: ImageSize
    usage_description: Optional[str] = None


class StyleOptions(BaseModel):
    color_palette: bool = True
    outline: bool = True
    detail: bool = True
    shading: bool = True


class GenerateImageV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def generate_image_v2(
    client: Any,
    description: str,
    image_size: Union[ImageSize, Dict[str, int]],
    seed: Optional[int] = None,
    no_background: bool = True,
    reference_images: Optional[
        Union[
            List[ReferenceImageItem],
            List[Dict[str, Any]],
        ]
    ] = None,
    style_image: Optional[Union[StyleImageItem, Dict[str, Any]]] = None,
    style_options: Optional[Union[StyleOptions, Dict[str, bool]]] = None,
) -> GenerateImageV2Response:
    """Generate multiple pixel art images from a text description.

    Args:
        client: The PixelLab client instance
        description: What to generate (1-2000 chars)
        image_size: Size of the generated images (width and height must be equal: 32, 64, 128, or 256)
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: True)
        reference_images: Up to 4 reference images for guidance
        style_image: Style reference image
        style_options: What to copy from style image (default: all True)

    Returns:
        GenerateImageV2Response containing multiple generated images and usage information

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
        - Up to 4 reference images can be provided
        - The endpoint consumes ~$0.18 worth of credits
    """
    request_data = {
        "description": description,
        "image_size": image_size,
        "no_background": no_background,
    }

    # Add optional parameters if provided
    if seed is not None:
        request_data["seed"] = seed

    if reference_images:
        processed_refs = []
        for ref in reference_images:
            if isinstance(ref, ReferenceImageItem):
                processed_refs.append(
                    {
                        "image": {"base64": ref.image.base64},
                        "size": ref.size,
                        "usage_description": ref.usage_description,
                    }
                )
            else:
                img_b64 = Base64Image.from_pil_image(ref["image"]).base64
                processed_refs.append(
                    {
                        "image": {"base64": img_b64},
                        "size": ref["size"],
                        "usage_description": ref.get("usage_description"),
                    }
                )
        request_data["reference_images"] = processed_refs

    if style_image:
        if isinstance(style_image, StyleImageItem):
            request_data["style_image"] = {
                "image": {"base64": style_image.image.base64},
                "size": style_image.size,
                "usage_description": style_image.usage_description,
            }
        else:
            img_b64 = Base64Image.from_pil_image(style_image["image"]).base64
            request_data["style_image"] = {
                "image": {"base64": img_b64},
                "size": style_image["size"],
                "usage_description": style_image.get("usage_description"),
            }

    if style_options:
        if isinstance(style_options, StyleOptions):
            request_data["style_options"] = style_options.model_dump()
        elif isinstance(style_options, dict):
            request_data["style_options"] = style_options

    try:
        response = requests.post(
            f"{client.base_url}/v2/generate-image-v2",
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

    return GenerateImageV2Response(**response.json())

