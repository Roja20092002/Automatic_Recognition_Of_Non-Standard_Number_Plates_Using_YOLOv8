import os

from detector import PlateDetector
from ocr import PlateOCR
from validation import PlateValidator


class ANPRPipeline:

    def __init__(self):

        self.detector = PlateDetector(
            model_path="model.pt",
            output_dir="outputs/detect"
        )

        self.ocr = PlateOCR()
        self.validator = PlateValidator()

    def process_image(self, image_path):

        crop_dir = self.detector.detect_image(image_path)

        if not os.path.exists(crop_dir) or not os.listdir(crop_dir):
            return [{
                "plate": "No plate detected",
                "full_text": "",
                "confidence": 0,
                "valid": None,
                "reason": "No plate detected",
                "crop_path": None
            }]

        results = []

        files = sorted(
            os.listdir(crop_dir),
            key=lambda x: os.path.getmtime(
                os.path.join(crop_dir, x)
            ),
            reverse=True
        )

        for file in files[:1]:

            crop_path = os.path.join(
                crop_dir,
                file
            )

            if not os.path.isfile(crop_path):
                continue

            ocr_result = self.ocr.extract_text(
                crop_path
            )

            plate_text = ocr_result["text"]
            full_text = ocr_result["full_text"]

            # No valid registration pattern found
            if not plate_text:

                valid = False
                reason = "Registration number not clearly identifiable"

                results.append({
                    "plate": "Not Found",
                    "full_text": full_text,
                    "confidence": ocr_result["confidence"],
                    "valid": valid,
                    "reason": reason,
                    "crop_path": os.path.relpath(
                        crop_path,
                        "outputs"
                    ).replace("\\", "/")
                })

                continue

            registration_valid = self.validator.is_valid_plate(
                plate_text
            )

            extra_text = full_text.replace(
                plate_text,
                ""
            )

            if not registration_valid:

                valid = False
                reason = "Registration format invalid"

            elif extra_text:

                valid = False
                reason = (
                    "Extra text detected: "
                    + extra_text
                )

            else:

                valid = True
                reason = "Plate compliant"

            results.append({
                "plate": plate_text,
                "full_text": full_text,
                "confidence": ocr_result["confidence"],
                "valid": valid,
                "reason": reason,
                "crop_path": os.path.relpath(
                    crop_path,
                    "outputs"
                ).replace("\\", "/")
            })

        return results

    def process_video(self, video_path):

        crop_dir, _ = self.detector.detect_video(
            video_path
        )

        if not os.path.exists(crop_dir):
            return []

        best_results = {}

        for root, dirs, files in os.walk(crop_dir):

            for file in files:

                crop_path = os.path.join(
                    root,
                    file
                )

                ocr_result = self.ocr.extract_text(
                    crop_path
                )

                if ocr_result["confidence"] < 0.1:
                    continue

                plate_text = ocr_result["text"]
                full_text = ocr_result["full_text"]

                if not plate_text:

                    valid = False
                    reason = (
                        "Registration number not clearly identifiable"
                    )

                    plate_key = "NOT_FOUND"

                else:

                    registration_valid = self.validator.is_valid_plate(
                        plate_text
                    )

                    extra_text = full_text.replace(
                        plate_text,
                        ""
                    )

                    if not registration_valid:

                        valid = False
                        reason = "Registration format invalid"

                    elif extra_text:

                        valid = False
                        reason = (
                            "Extra text detected: "
                            + extra_text
                        )

                    else:

                        valid = True
                        reason = "Plate compliant"

                    plate_key = plate_text

                score = ocr_result["confidence"]

                if valid:
                    score += 100

                if (
                    plate_key not in best_results
                    or score > best_results[plate_key]["score"]
                ):

                    best_results[plate_key] = {
                        "plate": (
                            plate_text
                            if plate_text
                            else "Not Found"
                        ),
                        "full_text": full_text,
                        "confidence": ocr_result["confidence"],
                        "valid": valid,
                        "reason": reason,
                        "score": score,
                        "crop_path": os.path.relpath(
                            crop_path,
                            "outputs"
                        ).replace("\\", "/")
                    }

        results = list(
            best_results.values()
        )

        results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return results


if __name__ == "__main__":

    pipeline = ANPRPipeline()

    results = pipeline.process_image(
        "uploads/testimg3.jpg"
    )

    print(results)