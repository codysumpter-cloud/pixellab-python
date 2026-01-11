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


class EditAnimationV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def edit_animation_v2(
    client: Any,
    description: str,
    frames: List[Dict[str, Any]],
    image_size: Union[ImageSize, Dict[str, int]],
    seed: Optional[int] = None,
    no_background: bool = False,
) -> EditAnimationV2Response:
    """Edit an animation by applying a description to all frames.

    Args:
        client: The PixelLab client instance
        description: What to add/change (e.g., "add a glowing red aura")
        frames: List of frame images (2-16 frames), each with:
            - image: PIL Image or {"base64": str}
            - size: {"width": int, "height": int}
        image_size: Size of the output images
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: False)

    Returns:
        EditAnimationV2Response containing edited frames and usage information

    Raises:
        ValueError: If authentication fails or validation errors occur
        requests.exceptions.HTTPError: For other HTTP-related errors
    """
    processed_frames = []
    for frame in frames:
        if isinstance(frame.get("image"), PIL.Image.Image):
            img_b64 = Base64Image.from_pil_image(frame["image"]).base64
        elif isinstance(frame.get("image"), dict):
            img_b64 = frame["image"].get("base64")
        else:
            img_b64 = Base64Image.from_pil_image(frame["image"]).base64

        processed_frames.append({
            "image": {"base64": img_b64},
            "size": frame["size"],
        })

    request_data = {
        "description": description,
        "frames": processed_frames,
        "image_size": image_size,
        "no_background": no_background,
    }

    if seed is not None:
        request_data["seed"] = seed

    try:
        response = requests.post(
            f"{client.base_url}/v2/edit-animation-v2",
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

    return EditAnimationV2Response(**response.json())
