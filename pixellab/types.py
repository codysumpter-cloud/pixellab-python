from typing import Literal, Union

CameraView = Literal["side", "low top-down", "high top-down"]
CameraViewV2 = Union[CameraView, Literal["none", "oblique"]]
Direction = Literal[
    "south",
    "south-east",
    "east",
    "north-east",
    "north",
    "north-west",
    "west",
    "south-west",
]
DirectionV2 = Union[Direction, Literal["none"]]
Outline = Literal[
    "single color black outline",
    "single color outline",
    "selective outline",
    "lineless",
]
Shading = Literal[
    "flat shading",
    "basic shading",
    "medium shading",
    "detailed shading",
    "highly detailed shading",
]

Detail = Literal["low detail", "medium detail", "highly detailed"]
