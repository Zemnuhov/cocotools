import json
from dataclasses import dataclass, field
from typing import List, Optional

from cocotools.models.annotation import CocoAnnotation
from cocotools.models.base_coco import BaseCocoObject
from cocotools.models.category import CocoCategory
from cocotools.models.image import CocoImage
from cocotools.models.info import CocoInfo
from cocotools.models.license import CocoLicense


@dataclass
class CocoDataset(BaseCocoObject):
    images: List[CocoImage] = field(default_factory=list)
    annotations: List[CocoAnnotation] = field(default_factory=list)
    categories: List[CocoCategory] = field(default_factory=list)
    info: Optional[CocoInfo] = None
    licenses: List[CocoLicense] = field(default_factory=list)

    @classmethod
    def from_json(cls, file_path: str) -> 'CocoDataset':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        def parse_list(class_type, data_list):
            return [class_type.from_dict(item) for item in data_list] if data_list else []

        info_obj = CocoInfo.from_dict(data.get('info', {})) if 'info' in data else None
        licenses_objs = parse_list(CocoLicense, data.get('licenses', []))
        images_objs = parse_list(CocoImage, data.get('images', []))
        annotations_objs = parse_list(CocoAnnotation, data.get('annotations', []))
        categories_objs = parse_list(CocoCategory, data.get('categories', []))

        dataset_metadata = {}
        standard_keys = {'images', 'annotations', 'categories', 'info', 'licenses'}
        for k, v in data.items():
            if k not in standard_keys:
                dataset_metadata[k] = v

        return cls(
            info=info_obj,
            licenses=licenses_objs,
            images=images_objs,
            annotations=annotations_objs,
            categories=categories_objs,
            metadata=dataset_metadata
        )


    def save_json(self, file_path: str, indent: int = 2) -> None:
        data_dict = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=indent)