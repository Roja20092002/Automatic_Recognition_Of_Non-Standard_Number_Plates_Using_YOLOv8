from flask import Flask, render_template, request, send_from_directory
import os

from pipeline import ANPRPipeline
from utils import save_results
from emailer import EmailNotifier

app = Flask(__name__)

pipeline = ANPRPipeline()
notifier = EmailNotifier()
alerted_plates = set()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        "uploads",
        filename
    )


@app.route("/outputs/<path:filename>")
def output_file(filename):
    return send_from_directory(
        "outputs",
        filename
    )


@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    filename = file.filename

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename # type: ignore
    ) # type: ignore

    file.save(filepath)

    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png"
    )

    video_extensions = (
        ".mp4",
        ".avi",
        ".mov"
    )

    # IMAGE
    if filename.lower().endswith(image_extensions): # type: ignore

        results = pipeline.process_image(
            filepath
        ) or []

    # VIDEO
    elif filename.lower().endswith(video_extensions): # type: ignore

        results = pipeline.process_video(
            filepath
        ) or []

        if results:

            results = sorted(
                results,
                key=lambda x: (
                    x["valid"],
                    x["confidence"]
                ),
                reverse=True
            )

            # keep only best result
            results = [results[0]]

    # UNSUPPORTED FILE
    else:

        results = [{
            "plate": "Unsupported file",
            "full_text": "",
            "confidence": 0,
            "valid": False,
            "reason": "Unsupported file",
            "crop_path": None
        }]

    # No result found
    if not results:

        results = [{
            "plate": "No plate detected",
            "full_text": "",
            "confidence": 0,
            "valid": False,
            "reason": "No plate detected",
            "crop_path": None
        }]

    save_results(results)

    for result in results:
        result["email_sent"] = False
        if (
            not result["valid"]
            and result.get("reason") not in [
                "No plate detected",
                "Unsupported file"
            ]
            and result["plate"] not in alerted_plates
        ):

            notifier.send_invalid_plate_alert(
                result.get("plate", ""),
                result.get("full_text", ""),
                result.get("reason", "")
            )

            result["email_sent"] = True

            alerted_plates.add(
                result["plate"]
            )

    return render_template(
        "result.html",
        results=results,
        image_path=filepath.replace("\\", "/")
    )


if __name__ == "__main__":
    app.run(
        debug=True
    )