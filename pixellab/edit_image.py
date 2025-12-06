from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Literal, Union, Dict

import PIL.Image
import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize

if TYPE_CHECKING:
    from .client import PixelLabClient


class Usage(BaseModel):
    type: Literal["usd"] = "usd"
    usd: float


class EditImageResponse(BaseModel):
    image: Base64Image
    usage: Optional[Usage] = None


def edit_image(
    client: Any,
    image: PIL.Image.Image,
    image_size: Union[ImageSize, Dict[str, int]],
    description: str,
    width: int,
    height: int,
    seed: int = 0,
    no_background: bool = True,
    text_guidance_scale: float = 8.0,
    color_image: Optional[PIL.Image.Image] = None,
) -> EditImageResponse:
    """Edit an existing pixel art image based on a text description.

    Args:
        client: The PixelLab client instance
        image: Reference image to edit (PIL Image)
        image_size: Size of the reference image (width and height in pixels)
        description: Text description of the edit to apply
        width: Target canvas width in pixels (16-400)
        height: Target canvas height in pixels (16-400)
        seed: Seed for reproducible generation (0 for random)
        no_background: Generate with transparent background (default: True)
        text_guidance_scale: How closely to follow the text description (1.0-10.0, default: 8.0)
        color_image: Optional color reference image for style guidance

    Returns:
        EditImageResponse containing the edited image and usage information

    Raises:
        ValueError: If authentication fails, validation errors occur, or constraints are violated
        requests.exceptions.HTTPError: For other HTTP-related errors

    Notes:
        - Reference image must be at least 16x16 pixels
        - Target canvas must be 16x16 to 400x400 pixels
        - Free tier users are limited to 200x200 pixels for target canvas
        - The endpoint consumes 1 generation or equivalent credits
    """
    # Convert PIL images to Base64
    image_base64 = Base64Image.from_pil_image(image)
    color_image_base64 = (
        Base64Image.from_pil_image(color_image) if color_image else None
    )

    request_data = {
        "image": image_base64.model_dump(),
        "image_size": image_size,
        "description": description,
        "width": width,
        "height": height,
        "seed": seed,
        "no_background": no_background,
        "text_guidance_scale": text_guidance_scale,
    }

    # Only add color_image if provided
    if color_image_base64:
        request_data["color_image"] = color_image_base64.model_dump()

    try:
        response = requests.post(
            f"{client.base_url}/v2/edit-image",
            headers=client.headers(),
            json=request_data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(error_detail)
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(error_detail)
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(error_detail)
        elif response.status_code == 402:
            error_detail = response.json().get("detail", "Insufficient resources")
            raise ValueError(error_detail)
        raise

    return EditImageResponse(**response.json())
