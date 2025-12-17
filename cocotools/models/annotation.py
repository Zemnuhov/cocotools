from dataclasses import dataclass, field
from typing import List, Union, Dict, Any
from cocotools.models.base_coco import BaseCocoObject


@dataclass(kw_only=True)
class CocoAnnotation(BaseCocoObject):
    id: int
    image_id: int
    category_id: int
    bbox: List[float] = field(default_factory=list)
    area: float = 0.0
    iscrowd: int = 0
    segmentation: Union[List[List[float]], Dict[str, Any]] = field(default_factory=list)