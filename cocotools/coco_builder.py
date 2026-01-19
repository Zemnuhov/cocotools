import dataclasses
from dataclasses import field
from typing import List, Union, Dict, Any

import shapely

from cocotools.models.annotation import CocoAnnotation
from cocotools.models.category import CocoCategory
from cocotools.models.dataset import CocoDataset
from cocotools.models.image import CocoImage

@dataclasses.dataclass
class ItemAnnotation:
    category: Union[int, str]
    segmentation: Union[List[List[float]], Dict[str, Any]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclasses.dataclass
class BuilderItem:
    file_name: str
    width: int
    height: int
    annotations: List[ItemAnnotation]
    metadata: dict = field(default_factory=dict)


class CocoBuilder:
    def __init__(self, categories: dict):
        self.dataset = None
        self.images = []
        self.annotations = []
        self.current_image_id = 0
        self.current_annotation_id = 0
        self.categories = categories  # Ожидается формат {"Name": ID}

    def _resolve_category_id(self, category_input: Union[int, str]) -> int:
        """Превращает строку или ID в валидный category_id из словаря."""
        if isinstance(category_input, int):
            return category_input

        if category_input not in self.categories:
            raise ValueError(f"Категория '{category_input}' не найдена в словаре билдера.")

        return self.categories[category_input]

    def _calculate_bbox(self, segmentation: Union[List[List[float]], Any]):
        if not isinstance(segmentation, list) or not segmentation:
            return [0, 0, 0, 0], 0.0

        all_points = [p for poly in segmentation for p in poly]
        x_coords = all_points[0::2]
        y_coords = all_points[1::2]

        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        w, h = max_x - min_x, max_y - min_y
        return [min_x, min_y, w, h]

    def _calculate_area(self, segmentation: Union[List[List[float]], Any]):
        polygon = shapely.Polygon(segmentation)
        return polygon.area

    def add_item(self, item: BuilderItem):
        image = CocoImage(
            id=self.current_image_id,
            file_name=item.file_name,
            width=item.width,
            height=item.height,
            metadata=item.metadata,
        )
        self.images.append(image)
        for ann in item.annotations:
            category_id = self._resolve_category_id(ann.category)
            bbox = self._calculate_bbox(ann.segmentation)
            area = self._calculate_area(ann.segmentation)
            coco_ann = CocoAnnotation(
                id=self.current_annotation_id,
                image_id=self.current_image_id,
                category_id=category_id,
                bbox=bbox,
                area=area,
                iscrowd=0,
                segmentation=ann.segmentation
            )
            self.annotations.append(coco_ann)
            self.current_annotation_id += 1
        self.current_image_id += 1

    def build_dataset(self) -> CocoDataset:
        categories_objs = [
            CocoCategory(id=cat_id, name=cat_name)
            for cat_name, cat_id in self.categories.items()
        ]
        self.dataset = CocoDataset(
            images=self.images,
            annotations=self.annotations,
            categories=categories_objs
        )

        return self.dataset