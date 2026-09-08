from typing import Union, List

from cocotools.coco_item import CocoItem, ItemAnnotation
from cocotools.models.annotation import CocoAnnotation
from cocotools.models.dataset import CocoDataset
from cocotools.models.image import CocoImage


class COCOWrapper:

    def __init__(self, dataset: CocoDataset):
        self.dataset = dataset
        self._annotation_by_img_id = {img.id: [] for img in dataset.images}
        for ann in dataset.annotations:
            if ann.image_id in self._annotation_by_img_id.keys():
                self._annotation_by_img_id[ann.image_id].append(ann)
        self._image_ids = [i.id for i in self.dataset.images]

    def get_image_ids(self) -> List[int]:
        return self._image_ids

    def get_coco_item_by_id(self, img_id: int) -> CocoItem:
        image = self.get_img_by_id(img_id)
        annotation = self.get_annotation_by_img(image)
        return CocoItem(
            file_name=image.file_name,
            width=image.width,
            height=image.height,
            annotations=[
                ItemAnnotation(
                    category=a.category_id,
                    segmentation=a.segmentation,
                    metadata=a.metadata)
                for a in annotation
            ],
            metadata=image.metadata
        )

    def get_img_by_id(self, img_id: int) -> CocoImage:
        return next((i for i in self.dataset.images if i.id == img_id), None)

    def get_annotation_by_img(self, img: Union[CocoImage, int]):
        return self._annotation_by_img_id[img.id if isinstance(img, CocoImage) else img]

    def get_img_by_filename(self, file_name: str) -> CocoImage:
        return next((i for i in self.dataset.images if i.file_name == file_name), None)

    def remove_image_by_id(self, img_id: int) -> CocoDataset:
        image = self.get_img_by_id(img_id)
        self.dataset.images.remove(image)
        return self.dataset
