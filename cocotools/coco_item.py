from dataclasses import dataclass, field
from typing import Union, List, Dict, Any


@dataclass
class ItemAnnotation:
    category: Union[int, str]
    segmentation: Union[List[List[float]], Dict[str, Any]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclass
class CocoItem:
    file_name: str
    width: int
    height: int
    annotations: List[ItemAnnotation]
    metadata: dict = field(default_factory=dict)