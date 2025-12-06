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


class EditImageItem(BaseModel):
    image: Base64Image
    width: int
    height: int


class ReferenceImageItem(BaseModel):
    image: Base64Image
    width: int
    height: int


class EditImagesV2Response(BaseModel):
    images: List[Base64Image]
    usage: Usage


def edit_images_v2(
    client: Any,
    edit_images: Union[List[EditImageItem], List[Dict[str, Any]]],
    image_size: Union[ImageSize, Dict[str, int]],
    method: Literal["edit_with_text", "edit_with_reference"] = "edit_with_text",
    description: Optional[str] = None,
    reference_image: Optional[Union[ReferenceImageItem, Dict[str, Any]]] = None,
    seed: Optional[int] = None,
    no_background: bool = False,
) -> EditImagesV2Response:
    """Edit pixel art images using text description or reference image.

    Args:
        client: The PixelLab client instance
        edit_images: Images to edit (1-16 depending on size)
        image_size: Size of the output images (32-256)
        method: Edit method - "edit_with_text" or "edit_with_reference" (default: "edit_with_text")
        description: Edit instruction (required if method="edit_with_text")
        reference_image: Reference image for editing (required if method="edit_with_reference")
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: False)

    Returns:
        EditImagesV2Response containing edited images and usage information

    Raises:
        ValueError: If authentication fails, validation errors occur, or constraints are violated
        requests.exceptions.HTTPError: For other HTTP-related errors

    Notes:
        Frame limits by size:
        - 32-64px: 16 frames (edit_with_text) or 15 frames (edit_with_reference)
        - 65-80px: 9 frames (edit_with_text) or 8 frames (edit_with_reference)
        - 81-128px: 4 frames (edit_with_text) or 3 frames (edit_with_reference)
        - 129-256px: 1 frame (edit_with_text only, edit_with_reference not supported)
        - The endpoint consumes ~$0.18 worth of credits
    """
    # Process edit_images
    processed_edit_images = []
    for img in edit_images:
        if isinstance(img, EditImageItem):
            processed_edit_images.append(
                {
                    "image": {"base64": img.image.base64},
                    "width": img.width,
                    "height": img.height,
                }
            )
        else:
            img_b64 = Base64Image.from_pil_image(img["image"]).base64
            processed_edit_images.append(
                {
                    "image": {"base64": img_b64},
                    "width": img["width"],
                    "height": img["height"],
                }
            )

    request_data = {
        "edit_images": processed_edit_images,
        "image_size": image_size,
        "method": method,
        "no_background": no_background,
    }

    # Add optional parameters if provided
    if seed is not None:
        request_data["seed"] = seed

    if method == "edit_with_text":
        if description is None:
            raise ValueError("description is required when method='edit_with_text'")
        request_data["description"] = description
    elif method == "edit_with_reference":
        if reference_image is None:
            raise ValueError(
                "reference_image is required when method='edit_with_reference'"
            )
        if isinstance(reference_image, ReferenceImageItem):
            request_data["reference_image"] = {
                "image": {"base64": reference_image.image.base64},
                "width": reference_image.width,
                "height": reference_image.height,
            }
        else:
            img_b64 = Base64Image.from_pil_image(reference_image["image"]).base64
            request_data["reference_image"] = {
                "image": {"base64": img_b64},
                "width": reference_image["width"],
                "height": reference_image["height"],
            }

    try:
        response = requests.post(
            f"{client.base_url}/v2/edit-images-v2",
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

    return EditImagesV2Response(**response.json())

