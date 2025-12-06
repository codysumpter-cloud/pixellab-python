from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Union, Dict

import PIL.Image
import requests
from pydantic import BaseModel

from .models import Base64Image, ImageSize

if TYPE_CHECKING:
    from .client import PixelLabClient


class Usage(BaseModel):
    type: Literal["usd"] = "usd"
    usd: float


class ConceptImageItem(BaseModel):
    image: Base64Image
    width: int
    height: int


class ReferenceImageItem(BaseModel):
    image: Base64Image
    width: int
    height: int


class Generate8RotationsV2Response(BaseModel):
    images: list[Base64Image]  # Always 8 images in order: S, SW, W, NW, N, NE, E, SE
    usage: Usage


def generate_8_rotations_v2(
    client: Any,
    image_size: Union[ImageSize, Dict[str, int]],
    method: Literal["rotate_character", "create_with_style", "create_from_concept"] = "rotate_character",
    concept_image: Optional[Union[ConceptImageItem, Dict[str, Any]]] = None,
    reference_image: Optional[Union[ReferenceImageItem, Dict[str, Any]]] = None,
    description: Optional[str] = None,
    style_description: Optional[str] = None,
    view: Literal["low top-down", "high top-down", "side"] = "low top-down",
    seed: Optional[int] = None,
    no_background: bool = True,
) -> Generate8RotationsV2Response:
    """Generate 8 directional views of a character or object.

    Args:
        client: The PixelLab client instance
        image_size: Size of the generated images (width and height must be equal, between 32 and 84)
        method: Generation method (default: "rotate_character")
            - "rotate_character": Rotate existing sprite (requires reference_image)
            - "create_from_concept": Create rotations from concept art (requires concept_image)
            - "create_with_style": Create new character matching style (requires description)
        concept_image: Concept art image (required for create_from_concept)
        reference_image: Image to rotate (required for rotate_character)
        description: Character description (max 2000 chars, required for create_with_style)
        style_description: Style description (max 500 chars)
        view: Camera view angle (default: "low top-down")
        seed: Seed for reproducibility (default: random)
        no_background: Remove background (default: True)

    Returns:
        Generate8RotationsV2Response containing 8 images in order: S, SW, W, NW, N, NE, E, SE

    Raises:
        ValueError: If authentication fails, validation errors occur, or constraints are violated
        requests.exceptions.HTTPError: For other HTTP-related errors

    Notes:
        - Image size must be square (width and height equal, between 32 and 84 inclusive)
        - Always returns exactly 8 images in directional order
        - Methods:
          - rotate_character: Rotate existing sprite (requires reference_image)
          - create_from_concept: Create rotations from concept art (requires concept_image)
          - create_with_style: Create new character matching style (requires description)
        - The endpoint consumes ~$0.18 worth of credits
    """
    request_data = {
        "image_size": image_size,
        "method": method,
        "view": view,
        "no_background": no_background,
    }

    # Add optional parameters if provided
    if seed is not None:
        request_data["seed"] = seed

    if description:
        request_data["description"] = description

    if style_description:
        request_data["style_description"] = style_description

    # Handle concept_image
    if concept_image:
        if isinstance(concept_image, ConceptImageItem):
            request_data["concept_image"] = {
                "image": {"base64": concept_image.image.base64},
                "width": concept_image.width,
                "height": concept_image.height,
            }
        else:
            img_b64 = Base64Image.from_pil_image(concept_image["image"]).base64
            request_data["concept_image"] = {
                "image": {"base64": img_b64},
                "width": concept_image["width"],
                "height": concept_image["height"],
            }

    # Handle reference_image
    if reference_image:
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

    # Validate image size (must be square, between 32 and 84)
    width = image_size["width"]
    height = image_size["height"]
    
    if width != height:
        raise ValueError("image_size width and height must be equal (square images only)")
    if not (32 <= width <= 84):
        raise ValueError(f"image_size must be between 32 and 84 (inclusive), got {width}x{height}")

    # Validate required parameters based on method
    if method == "rotate_character":
        if not reference_image:
            raise ValueError("reference_image is required when method='rotate_character'")
    elif method == "create_from_concept":
        if not concept_image:
            raise ValueError("concept_image is required when method='create_from_concept'")
    elif method == "create_with_style":
        if not description:
            raise ValueError("description is required when method='create_with_style'")

    try:
        response = requests.post(
            f"{client.base_url}/v2/generate-8-rotations-v2",
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

    return Generate8RotationsV2Response(**response.json())

