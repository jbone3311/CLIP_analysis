import os
import json
import hashlib
import datetime
from PIL import Image
import imagehash
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

def compute_hashes(image: Image.Image) -> Dict[str, str]:
    """Compute perceptual hashes of the image."""
    hashes = {
        'average_hash': str(imagehash.average_hash(image)),
        'perceptual_hash': str(imagehash.phash(image)),
        'difference_hash': str(imagehash.dhash(image)),
    }
    return hashes

def compute_cryptographic_hashes(image_path: str) -> Dict[str, str]:
    """Compute cryptographic hashes of the image file."""
    hashes = {}
    with open(image_path, 'rb') as f:
        file_data = f.read()
        hashes['md5'] = hashlib.md5(file_data).hexdigest()
        hashes['sha1'] = hashlib.sha1(file_data).hexdigest()
        hashes['sha256'] = hashlib.sha256(file_data).hexdigest()
    return hashes

def encode_image(image: Image.Image) -> str:
    """Encode image to base64 string after resizing."""
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_string

def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize image to a maximum dimension."""
    original_size = image.size
    image.thumbnail((max_size, max_size), Image.ANTIALIAS)
    logging.debug(f"Resized image from {original_size} to {image.size}")
    return image

def generate_thumbnail(image: Image.Image, size: tuple = (128, 128)) -> Image.Image:
    """Generate a thumbnail of the image."""
    thumbnail = image.copy()
    thumbnail.thumbnail(size, Image.ANTIALIAS)
    return thumbnail

def get_image_metadata(image_path: str) -> Dict[str, Any]:
    """Extract metadata and compute hashes for an image."""
    metadata = {}
    date_added = datetime.datetime.now().isoformat()
    metadata['filename'] = os.path.basename(image_path)
    metadata['date_added'] = date_added

    # Cryptographic hashes
    crypto_hashes = compute_cryptographic_hashes(image_path)
    unique_hash = crypto_hashes['sha256']  # Define unique hash
    metadata['unique_hash'] = unique_hash
    metadata['cryptographic_hashes'] = crypto_hashes

    with Image.open(image_path) as img:
        # Resize image to maximum 1024 pixels
        img_resized = resize_image(img)
        width, height = img_resized.size
        dpi = img_resized.info.get('dpi', (72, 72))
        metadata['width'] = width
        metadata['height'] = height
        metadata['dpi'] = dpi

        # Perceptual hashes
        perceptual_hashes = compute_hashes(img_resized)
        metadata['perceptual_hashes'] = perceptual_hashes

        # Generate and encode thumbnail
        thumbnail = generate_thumbnail(img_resized)
        metadata['thumbnail'] = encode_image(thumbnail)

    return metadata

def save_metadata_to_json(metadata: Dict[str, Any], output_path: str):
    """Save metadata to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    logging.info(f"Saved metadata to {output_path}")

def process_image_file(image_path: str, output_directory: str):
    """Process an image file and save metadata."""
    metadata = get_image_metadata(image_path)
    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_DATA.json"
    output_path = os.path.join(output_directory, output_filename)

    save_metadata_to_json(metadata, output_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process images and extract metadata.")
    parser.add_argument("image_path", help="Path to the image file.")
    parser.add_argument("--output_directory", help="Directory to save the metadata JSON file.", default=".")
    args = parser.parse_args()

    process_image_file(args.image_path, args.output_directory)