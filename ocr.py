import re
import easyocr
import cv2


class PlateOCR:

    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def extract_text(self, image_path):

        img = cv2.imread(image_path)

        if img is None:
            raise FileNotFoundError(
                f"Could not read image: {image_path}"
            )

        img = cv2.resize(
            img,
            None,
            fx=4,
            fy=4,
            interpolation=cv2.INTER_CUBIC
        )

        results = self.reader.readtext(img)

        texts = []
        confidences = []

        for detection in results:

            text = detection[1].upper().strip()

            texts.append(text)

            confidences.append(
                float(detection[2])
            )

        full_text = "".join(texts)

        full_text = re.sub(
            r'[^A-Za-z0-9]',
            '',
            full_text
        ).upper()

        full_text = full_text.replace("Z", "4")
        full_text = full_text.replace("L", "4")
        full_text = full_text.replace("I", "1")
        full_text = full_text.replace("Q", "4")

        matches = re.findall(
            r'[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}',
            full_text
        )

        if matches:
            plate_text = matches[0]
        else:
            plate_text = ""

        avg_conf = (
            sum(confidences) / len(confidences)
            if confidences else 0
        )

        return {
            "text": plate_text,
            "full_text": full_text,
            "segments": texts,
            "confidence": round(avg_conf, 3)
        }


if __name__ == "__main__":

    ocr = PlateOCR()

    result = ocr.extract_text(
        "outputs/detect/image/crops/LicensePlate/testimg3.jpg"
    )

    print(result)