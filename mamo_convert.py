import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
import pydicom

from cocotools.coco_builder import CocoBuilder
from transliterate import translit

from cocotools.coco_item import CocoItem, ItemAnnotation

ANNOTATION_TYPE = "mgdcmfreehandlabels"


def get_dicom_metadata(
    dicom_dict: List[str], data_path: Path
) -> List[pydicom.dataset.FileDataset]:
    datasets = []
    for dic_path_str in dicom_dict:
        raw_path = Path(dic_path_str)
        full_path = data_path.joinpath(*raw_path.parts[3:])

        if full_path.exists():
            ds = pydicom.dcmread(full_path, stop_before_pixels=True)
            datasets.append({"dicom": ds, "filename": Path().joinpath(*raw_path.parts[3:])})
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
        for data in dicoms:
            ds = data["dicom"]
            filename = data["filename"]
            view = getattr(ds, "ViewPosition", "Unknown")
            side = getattr(ds, "ImageLaterality", "Unknown")
            pixel_spacing = getattr(ds, "PixelSpacing", None)
            key = f"{view}_{side}"

            info_by_side[key] = {
                "file_name": f"{filename}",
                "view": view,
                "side": side,
                "width": getattr(ds, "Rows", 0),
                "height": getattr(ds, "Columns", 0),
                "annotation_creator": current_ann.get("created_username"),
                "created_at": current_ann.get("created_at"),
                "annotation": [],
                "pixel_spacing": pixel_spacing,
            }

        process_annotations(current_ann.get("result", []), info_by_side)
        valid_items = [v for v in info_by_side.values() if v["annotation"]]
        final_result.extend(valid_items)

    return final_result

def rec_search(path: Path):
    if path.is_dir():
        for i in path.iterdir():
            rec_search(i)
    else:
        if path.suffix == ".json":
            res.append(
                {
                    "annotation": path,
                    "data": Path("/home/karpulevich_z/mammoannotate_files"),
                }
            )



if __name__ == "__main__":
    res = []
    rec_search(Path("/home/karpulevich_z/Segmentation_markup_02_09_2026"))
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
    for i in res:
        result_list = parse_json(
            str(i["annotation"]),
            str(i["data"]),
        )
        for item in result_list:
            builder.add_item(
                CocoItem(
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
                        ItemAnnotation(
                            category=ann["class"],
                            segmentation=(np.array(ann["points"])/float(item.get("pixel_spacing")[0])).tolist()
                            if isinstance(item.get("pixel_spacing"), pydicom.multival.MultiValue)
                            else ann["points"],
                        )
                        for ann in item["annotation"]
                    ],
                )
            )
    dataset = builder.build_dataset()
    dataset.save_json("/home/karpulevich_z/mammo_data_new/annotation/coco_Segmentation_markup_02_09_2026.json")
