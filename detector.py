import os
from ultralytics import YOLO
import shutil

class PlateDetector:

    def __init__(self, model_path: str, output_dir: str):
        self.model = YOLO(model_path)
        self.output_dir = os.path.abspath(output_dir)

    def detect_image(self, image_path: str, conf: float = 0.7):

        crop_folder = os.path.join(
            self.output_dir,
            "image",
            "crops",
            "LicensePlate"
        )

        if os.path.exists(crop_folder):
            shutil.rmtree(crop_folder)

        self.model.predict(
            source=image_path,
            conf=conf,
            save=True,
            save_crop=True,
            project=self.output_dir,
            name="image",
            exist_ok=True
        )

        crop_dir = os.path.join(
            self.output_dir,
            "image",
            "crops",
            "LicensePlate"
        )

        return crop_dir

    def detect_video(self, video_path: str, conf: float = 0.7):

        self.model.track(
            source=video_path,
            conf=conf,
            save=True,
            save_crop=True,
            project=self.output_dir,
            name="video",
            exist_ok=True
        )

        crop_dir = os.path.join(
            self.output_dir,
            "video",
            "crops",
            "LicensePlate"
        )

        label_dir = os.path.join(
            self.output_dir,
            "video",
            "labels"
        )

        return crop_dir, label_dir


if __name__ == "__main__":

    detector = PlateDetector(
        model_path="model.pt",
        output_dir="outputs/detect"
    )

    crops = detector.detect_image(
        "uploads/testimg3.jpg"
    )

    print("Crops saved at:", crops)