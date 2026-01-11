from __future__ import annotations

from pydantic import BaseModel

from .settings import settings


class PixelLabClient(BaseModel):
    secret: str
    base_url: str = "https://api.pixellab.ai"

    @classmethod
    def from_env(cls) -> PixelLabClient:
        return cls(**settings(env_file=None).model_dump(exclude_none=True))

    @classmethod
    def from_env_file(cls, env_file: str) -> PixelLabClient:
        return cls(**settings(env_file=env_file).model_dump(exclude_none=True))

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token()}",
        }

    def headers(self):
        return {"Authorization": f"Bearer {self.secret}"}

    from .animate_with_skeleton import animate_with_skeleton
    from .animate_with_text import animate_with_text
    from .animate_with_text_v2 import animate_with_text_v2
    from .edit_image import edit_image
    from .edit_images_v2 import edit_images_v2
    from .edit_animation_v2 import edit_animation_v2
    from .estimate_skeleton import estimate_skeleton
    from .generate_image_bitforge import generate_image_bitforge
    from .generate_image_pixflux import generate_image_pixflux
    from .generate_image_v2 import generate_image_v2
    from .generate_ui_v2 import generate_ui_v2
    from .generate_with_style_v2 import generate_with_style_v2
    from .generate_8_rotations_v2 import generate_8_rotations_v2
    from .rotate4_with_template import rotate4_with_template
    from .rotate8_with_template import rotate8_with_template
    from .animate_with_template import animate_with_template
    from .generate_tileset import generate_tileset
    from .get_balance import get_balance
    from .inpaint import inpaint
    from .inpaint_v3 import inpaint_v3
    from .interpolation_v2 import interpolation_v2
    from .transfer_outfit_v2 import transfer_outfit_v2
    from .rotate import rotate
    from .generate_isometric_tile import generate_isometric_tile
    from .resize import resize
    from .image_to_pixelart import image_to_pixelart
