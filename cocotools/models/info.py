from dataclasses import dataclass
from typing import Optional

from cocotools.models.base_coco import BaseCocoObject


@dataclass(kw_only=True)
class CocoInfo(BaseCocoObject):
    description: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None
    contributor: Optional[str] = None
    date_created: Optional[str] = None