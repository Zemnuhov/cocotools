from typing import Union, List

from cocotools.models.annotation import CocoAnnotation
from cocotools.models.dataset import CocoDataset
from cocotools.models.image import CocoImage


class COCOWrapper:

    def __init__(self, dataset: CocoDataset):
        self.dataset = dataset
        self._annotation_by_img_id = {img.id: [] for img in dataset.images}
        for ann in dataset.annotations:
            self._annotation_by_img_id[ann.image_id].append(ann)


    def get_annotation_by_img(self, img: Union[CocoImage, int]):
        return self._annotation_by_img_id[img.id if isinstance(img, CocoImage) else img]

    def add_item(self, image: CocoImage, annotations: List[CocoAnnotation]):
        if image.id in self._annotation_by_img_id:
            image.id = max(self._annotation_by_img_id.keys()) + 1
        for ann in annotations:
            if ann.image_id != image.id:
                ann.image_id = image.id

        self.dataset.images.append(image)
        self.dataset.annotations.extend(annotations)
        self._annotation_by_img_id[image.id] = annotations


