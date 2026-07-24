from pathlib import Path
from io import BytesIO
import base64

from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

INPUT_DIR = Path("./input")
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPT = """
Edit this food photograph while preserving the exact meal and ingredients. Do not change portion size or ingredients.
Make it appear as if photographed in a professional restaurant studio.
Soft diffused lighting from the upper left. Neutral white balance. Natural shadows. Keep colors realistic.
Slight overhead angle (about 30 degrees).
Center the plate. Ensure the entire rim and middle of the plate is visible.
Never crop any part of the plate especially the side. Preserve the exact plate especially the dodecagon shape. The plate is wide.
The full plate fits the image without missing parts. Do not crop the plate!
"""
TARGET_SIZE = (300, 300)

client = OpenAI()


def edit_image(path: Path) -> Image.Image:
    with open(path, "rb") as image_file:
        result = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=PROMPT,
            size="1024x1024",
            background="transparent",
            quality="medium",
        )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    return Image.open(BytesIO(image_bytes)).convert("RGBA")


for image_path in sorted(INPUT_DIR.glob("*.png")):
    output_path = OUTPUT_DIR / image_path.name
    if output_path.exists():
        print(f"Skipping {image_path.name}")
        continue

    print(f"Editing {image_path.name}")

    try:
        img = edit_image(image_path)
        img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        img.save(output_path)

    except Exception as e:
        print(f"Failed: {image_path.name}")
        print(e)