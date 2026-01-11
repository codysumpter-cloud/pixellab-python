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


class InpaintV3Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def inpaint_v3(
    client: Any,
    description: str,
    inpainting_image: Dict[str, Any],
    mask_image: Dict[str, Any],
    context_image: Optional[Dict[str, Any]] = None,
    bounding_box: Optional[Dict[str, int]] = None,
    seed: Optional[int] = None,
    no_background: bool = False,
) -> InpaintV3Response:
    """Inpaint regions of an image based on a mask.

    Args:
        client: The PixelLab client instance
        description: What to generate in the masked region
        inpainting_image: Image to inpaint (32-256px):
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        mask_image: Mask defining regions to generate (white=generate, black=preserve):
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        context_image: Optional larger context image (up to 1024px):
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        bounding_box: Optional bounding box for context:
            - x: int
            - y: int
            - width: int
            - height: int
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: False)

    Returns:
        InpaintV3Response containing inpainted images and usage information

    Raises:
        ValueError: If authentication fails or validation errors occur
        requests.exceptions.HTTPError: For other HTTP-related errors
    """
    # Process inpainting image
    if isinstance(inpainting_image.get("image"), PIL.Image.Image):
        inpaint_b64 = Base64Image.from_pil_image(inpainting_image["image"]).base64
    elif isinstance(inpainting_image.get("image"), dict):
        inpaint_b64 = inpainting_image["image"].get("base64")
    else:
        inpaint_b64 = Base64Image.from_pil_image(inpainting_image["image"]).base64

    # Process mask image
    if isinstance(mask_image.get("image"), PIL.Image.Image):
        mask_b64 = Base64Image.from_pil_image(mask_image["image"]).base64
    elif isinstance(mask_image.get("image"), dict):
        mask_b64 = mask_image["image"].get("base64")
    else:
        mask_b64 = Base64Image.from_pil_image(mask_image["image"]).base64

    request_data = {
        "description": description,
        "inpainting_image": {
            "image": {"base64": inpaint_b64},
            "size": inpainting_image["size"],
        },
        "mask_image": {
            "image": {"base64": mask_b64},
            "size": mask_image["size"],
        },
        "no_background": no_background,
    }

    # Process optional context image
    if context_image:
        if isinstance(context_image.get("image"), PIL.Image.Image):
            context_b64 = Base64Image.from_pil_image(context_image["image"]).base64
        elif isinstance(context_image.get("image"), dict):
            context_b64 = context_image["image"].get("base64")
        else:
            context_b64 = Base64Image.from_pil_image(context_image["image"]).base64

        request_data["context_image"] = {
            "image": {"base64": context_b64},
            "size": context_image["size"],
        }

    if bounding_box:
        request_data["bounding_box"] = bounding_box

    if seed is not None:
        request_data["seed"] = seed

    try:
        response = requests.post(
            f"{client.base_url}/v2/inpaint-v3",
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

    return InpaintV3Response(**response.json())
