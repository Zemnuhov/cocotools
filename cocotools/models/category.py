from dataclasses import dataclass
from typing import Optional

from cocotools.models.base_coco import BaseCocoObject


@dataclass(kw_only=True)
class CocoCategory(BaseCocoObject):
    id: int
    name: str
    supercategory: Optional[str] = None