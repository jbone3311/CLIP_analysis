import base64
import hashlib
import logging
from typing import Optional, Tuple
from PIL import Image, UnidentifiedImageError
from io import BytesIO

def generate_unique_code(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except IOError as e:
        logging.error(f"Error generating unique code for {image_path}: {str(e)}")
        return None

def resize_image(image: Image.Image, max_size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """Resize the image to fit within max_size while maintaining aspect ratio.

    Args:
        image (PIL.Image): Image to resize.
        max_size (tuple): Maximum width and height.

    Returns:
        PIL.Image: Resized image.
    """
    image.thumbnail(max_size, Image.LANCZOS)
    return image

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encode an image file to a base64 string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        Optional[str]: Base64 encoded string of the image, or None if an error occurs.
    """
    try:
        with Image.open(image_path) as img:
            img = resize_image(img)  # Resize the image before encoding
            with BytesIO() as imgio:
                img.save(imgio, 'JPEG')
                imgio.seek(0)
                data = base64.b64encode(imgio.getvalue())
                return data.decode('utf8')
    except FileNotFoundError as e:
        logging.error("Image file not found: %s - %s", image_path, e)
    except UnidentifiedImageError as e:
        logging.error("Cannot identify image file: %s - %s", image_path, e)
    except Exception as e:
        logging.error("Error encoding image to base64: %s", e)
    return None

def process_image_for_analysis(image_path: str) -> Optional[str]:
    """Process an image for analysis by resizing and converting to JPEG if needed.

    Args:
        image_path (str): Path to the image file.

    Returns:
        Optional[str]: Base64 encoded string of the processed image, or None if an error occurs.
    """
    try:
        with Image.open(image_path) as img:
            # Check if the image is already 512x512 or smaller and in JPEG format
            if img.size[0] <= 512 and img.size[1] <= 512 and img.format == 'JPEG':
                return encode_image_to_base64(image_path)
            else:
                # Resize and convert to JPEG
                img = resize_image(img)
                with BytesIO() as imgio:
                    img.save(imgio, 'JPEG')
                    imgio.seek(0)
                    data = base64.b64encode(imgio.getvalue())
                    return data.decode('utf8')
    except FileNotFoundError as e:
        logging.error("Image file not found: %s - %s", image_path, e)
    except UnidentifiedImageError as e:
        logging.error("Cannot identify image file: %s - %s", image_path, e)
    except Exception as e:
        logging.error("Error processing image for analysis: %s", e)
    return None