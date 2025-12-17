from dataclasses import dataclass
from typing import Optional

from cocotools.models.base_coco import BaseCocoObject


@dataclass(kw_only=True)
class CocoImage(BaseCocoObject):
    id: int
    file_name: str
    height: int
    width: int
    license: Optional[int] = None
    date_captured: Optional[str] = None
    coco_url: Optional[str] = None
    flickr_url: Optional[str] = None