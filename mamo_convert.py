import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import pydicom

from cocotools.coco_builder import CocoBuilder, BuilderItem, ItemAnnotation

ANNOTATION_TYPE = "mgdcmfreehandlabels"


def get_dicom_metadata(
    dicom_dict: List[str], data_path: Path
) -> List[pydicom.dataset.FileDataset]:
    datasets = []
    for dic_path_str in dicom_dict:
        raw_path = Path(dic_path_str)
        full_path = data_path / raw_path.parent.stem / raw_path.name

        if full_path.exists():
            ds = pydicom.dcmread(full_path, stop_before_pixels=True)
            datasets.append(ds)
    return datasets


def process_annotations(results: List[Dict], info_by_side: Dict[str, Dict]):
    for item in results:
        if item.get("type") != ANNOTATION_TYPE:
            continue
        val = item["value"]
        view = val["view_position"].upper()
        side = val["laterality"].upper()
        key = f"{view}_{side}"

        if key in info_by_side:
            info_by_side[key]["annotation"].append(
                {
                    "points": val["points"],
                    "class": val[ANNOTATION_TYPE][0],
                }
            )


def parse_json(
    label_studio_annotation: str, data_path_str: str
) -> List[Dict[str, Any]]:
    annotation_path = Path(label_studio_annotation)
    data_path = Path(data_path_str)
    with annotation_path.open("r", encoding="utf-8") as f:
        data_list = json.load(f)
    final_result = []
    for item in data_list:
        data_part = item.get("data", {})
        annotations = item.get("annotations", [])
        if not annotations:
            continue
        current_ann = annotations[0]
        dicoms = get_dicom_metadata(data_part.get("dicom", []), data_path)
        if not dicoms:
            continue
        case_id = data_part.get("case", "unknown")
        info_by_side = {}
        for ds in dicoms:
            view = getattr(ds, "ViewPosition", "Unknown")
            side = getattr(ds, "ImageLaterality", "Unknown")
            key = f"{view}_{side}"

            info_by_side[key] = {
                "file_name": f"{case_id}/{Path(ds.filename).name}",
                "view": view,
                "side": side,
                "width": getattr(ds, "Rows", 0),
                "height": getattr(ds, "Columns", 0),
                "annotation_creator": current_ann.get("created_username"),
                "created_at": current_ann.get("created_at"),
                "annotation": [],
            }

        process_annotations(current_ann.get("result", []), info_by_side)
        valid_items = [v for v in info_by_side.values() if v["annotation"]]
        final_result.extend(valid_items)

    return final_result


if __name__ == "__main__":
    result_list = parse_json(
        "D:/All aug/blokhina_segm/Иванкина 2 v1/annotations-18-26-at-2025-05-13T09_21_53.json",
        "D:/All aug/blokhina/data",
    )
    builder = CocoBuilder(
        categories={
            "Злокачественные образование": 1,
            "Доброкачественное образование": 2,
            "Нарушение архитектоники": 3,
            "Доброкачественные кальцинаты": 4,
            "Злокачественные кальцинаты": 5,
            "Утолщение кожи": 6,
        }
    )
    for item in result_list:
        builder.add_item(
            BuilderItem(
                file_name=item["file_name"],
                width=item["width"],
                height=item["height"],
                metadata={
                    "view": item["view"],
                    "side": item["side"],
                    "annotation_creator": item["annotation_creator"],
                    "created_at": item["created_at"],
                },
                annotations=[
                    ItemAnnotation(category=ann["class"], segmentation=ann["points"])
                    for ann in item["annotation"]
                ],
            )
        )
    dataset = builder.build_dataset()
    dataset.save_json("C:/Users/zemnu/PycharmProjects/cocotools/test.json")
