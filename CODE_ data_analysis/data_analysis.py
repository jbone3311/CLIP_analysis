import os
import json
import uuid
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import piexif
from xml.dom import minidom
from format import (
    A1111,
    EasyDiffusion,
    InvokeAI,
    NovelAI,
    ComfyUI,
    DrawThings,
    SwarmUI,
    Fooocus,
)

PARAMETER_PLACEHOLDER = None

class ImageDataReader:
    def __init__(self, file, is_txt: bool = False):
        self._height = None
        self._width = None
        self._info = {}
        self._positive = ""
        self._negative = ""
        self._positive_sdxl = {}
        self._negative_sdxl = {}
        self._setting = ""
        self._raw = ""
        self._tool = ""
        self._parameter_key = ["model", "sampler", "seed", "cfg", "steps", "size"]
        self._parameter = dict.fromkeys(self._parameter_key, PARAMETER_PLACEHOLDER)
        self._is_txt = is_txt
        self._is_sdxl = False
        self._format = ""
        self._parser = None
        self.read_data(file)

    def read_data(self, file):
        print(f"Reading data from file: {file}")  # Debug print

        if self._is_txt:
            self._raw = file.read()
            self._parser = A1111(raw=self._raw)
            return
        with Image.open(file) as f:
            self._width = f.width
            self._height = f.height
            self._info = f.info
            self._format = f.format

            print(f"Image width: {self._width}")  # Debug print
            print(f"Image height: {self._height}")  # Debug print
            print(f"Image info: {self._info}")  # Debug print
            print(f"Image format: {self._format}")  # Debug print

            # swarm legacy format
            try:
                exif = json.loads(f.getexif().get(0x0110))
                if "sui_image_params" in exif:
                    self._tool = "StableSwarmUI"
                    self._parser = SwarmUI(info=exif)
            except TypeError:
                if f.format == "PNG":
                    if "parameters" in self._info:
                        # swarm format
                        if "sui_image_params" in self._info.get("parameters"):
                            self._tool = "StableSwarmUI"
                            self._parser = SwarmUI(raw=self._info.get("parameters"))
                        # a1111 png compatible format
                        else:
                            if "prompt" in self._info:
                                self._tool = "ComfyUI\n(A1111 compatible)"
                            else:
                                self._tool = "A1111 webUI"
                            self._parser = A1111(info=self._info)
                    # easydiff png format
                    elif (
                        "negative_prompt" in self._info
                        or "Negative Prompt" in self._info
                    ):
                        self._tool = "Easy Diffusion"
                        self._parser = EasyDiffusion(info=self._info)
                    # invokeai3 format
                    elif "invokeai_metadata" in self._info:
                        self._tool = "InvokeAI"
                        self._parser = InvokeAI(info=self._info)
                    # invokeai2 format
                    elif "sd-metadata" in self._info:
                        self._tool = "InvokeAI"
                        self._parser = InvokeAI(info=self._info)
                    # invokeai legacy dream format
                    elif "Dream" in self._info:
                        self._tool = "InvokeAI"
                        self._parser = InvokeAI(info=self._info)
                    # novelai format
                    elif self._info.get("Software") == "NovelAI":
                        self._tool = "NovelAI"
                        self._parser = NovelAI(
                            info=self._info, width=self._width, height=self._height
                        )
                    # comfyui format
                    elif "prompt" in self._info:
                        self._tool = "ComfyUI"
                        self._parser = ComfyUI(
                            info=self._info, width=self._width, height=self._height
                        )
                    # fooocus format
                    elif "Comment" in self._info:
                        try:
                            self._tool = "Fooocus"
                            self._parser = Fooocus(
                                info=json.loads(self._info.get("Comment"))
                            )
                        except Exception:
                            print("Fooocus format error")
                    # draw things format
                    elif "drawthings" in self._info:
                        try:
                            self._tool = "Draw Things"
                            self._parser = DrawThings(
                                info=json.loads(self._info.get("drawthings"))
                            )
                        except Exception:
                            print("Draw things format error")
                        print("Unknown format")

                        if "XML:com.adobe.xmp" in self._info:
                            try:
                                data = minidom.parseString(
                                    self._info.get("XML:com.adobe.xmp")
                                )
                                data_json = json.loads(
                                    data.getElementsByTagName("exif:UserComment")[0]
                                    .childNodes[1]
                                    .childNodes[1]
                                    .childNodes[0]
                                    .data
                                )
                                self._tool = "Draw Things"
                                self._parser = DrawThings(info=data_json)
                            except Exception:
                                print("Draw things format error")
                        elif f.format in ["JPEG", "WEBP"]:
                            if "comment" in self._info:
                                try:
                                    self._tool = "Fooocus"
                                    self._parser = Fooocus(
                                        info=json.loads(self._info.get("comment"))
                                    )
                                except Exception:
                                    print("Fooocus format error")
                else:
                    try:
                        exif = piexif.load(self._info.get("exif")) or {}
                        user_comment = exif.get("Exif").get(
                            piexif.ExifIFD.UserComment
                        )
                    except TypeError:
                        print("empty jpeg")
                    except Exception:
                        pass
                    else:
                        # swarm format
                        if "sui_image_params" in user_comment[8:].decode("utf-16"):
                            self._tool = "StableSwarmUI"
                            self._parser = SwarmUI(
                                raw=user_comment[8:].decode("utf-16")
                            )
                        else:
                            self._raw = piexif.helper.UserComment.load(user_comment)
                            # easydiff jpeg and webp format
                            if self._raw[0] == "{":
                                self._tool = "Easy Diffusion"
                                self._parser = EasyDiffusion(raw=self._raw)
                            # a1111 jpeg and webp format
                            else:
                                self._tool = "A1111 webUI"
                                self._parser = A1111(raw=self._raw)

    @staticmethod
    def remove_data(image_file):
        with Image.open(image_file) as f:
            image_data = list(f.getdata())
            image_without_exif = Image.new(f.mode, f.size)
            image_without_exif.putdata(image_data)
            return image_without_exif

    @staticmethod
    def save_image(image_path, new_path, image_format, data=None):
        metadata = None
        if data:
            match image_format:
                case "PNG":
                    metadata = PngInfo()
                    metadata.add_text("parameters", data)
                case "JPEG" | "WEBP":
                    metadata = piexif.dump(
                        {
                            "Exif": {
                                piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(
                                    data, encoding="unicode"
                                )
                            },
                        }
                    )

        with Image.open(image_path) as f:
            try:
                match image_format:
                    case "PNG":
                        if data:
                            f.save(new_path, pnginfo=metadata)
                        else:
                            f.save(new_path)
                    case "JPEG":
                        f.save(new_path, quality="keep")
                        if data:
                            piexif.insert(metadata, str(new_path))
                    case "WEBP":
                        f.save(new_path, quality=100, lossless=True)
                        if data:
                            piexif.insert(metadata, str(new_path))
            except:
                print("Save error")

    def prompt_to_line(self):
        return self._parser.prompt_to_line()

    @property
    def height(self):
        return self._parser.height

    @property
    def width(self):
        return self._parser.width

    @property
    def info(self):
        return self._info

    @property
    def positive(self):
        return self._parser.positive

    @property
    def negative(self):
        return self._parser.negative

    @property
    def positive_sdxl(self):
        return self._parser.positive_sdxl

    @property
    def negative_sdxl(self):
        return self._parser.negative_sdxl

    @property
    def setting(self):
        return self._parser.setting

    @property
    def raw(self):
        return self._parser.raw

    @property
    def tool(self):
        return self._tool

    @property
    def parameter(self):
        return self._parser.parameter

    @property
    def format(self):
        return self._format

    @property
    def is_sdxl(self):
        return self._parser.is_sdxl

    @property
    def props(self):
        return self._parser.props


def process_images(directory):
    """
    Process images in the specified directory and save metadata to JSON files.
    """
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_path = os.path.join(dirpath, filename)
                json_output_path = os.path.join(dirpath, 'json', f"{filename.split('.')[0]}_metadata.json")

                # Ensure the 'json' subdirectory exists
                os.makedirs(os.path.join(dirpath, 'json'), exist_ok=True)

                # Process the image and extract metadata
                reader = ImageDataReader(image_path)
                metadata = {
                    "id": str(uuid.uuid4()),  # Unique identifier
                    "filename": filename,
                    "height": reader.height,
                    "width": reader.width,
                    "info": reader.info,
                    "positive": reader.positive,
                    "negative": reader.negative,
                    "positive_sdxl": reader.positive_sdxl,
                    "negative_sdxl": reader.negative_sdxl,
                    "setting": reader.setting,
                    "raw": reader.raw,
                    "tool": reader.tool,
                    "parameter": reader.parameter,
                    "format": reader.format,
                    "is_sdxl": reader.is_sdxl,
                    "props": reader.props,
                }

                # Save the metadata to a JSON file
                with open(json_output_path, 'w', encoding='utf-8') as json_file:
                    json.dump(metadata, json_file, ensure_ascii=False, indent=4)

                print(f"Processed and saved metadata for: {filename}")


if __name__ == "__main__":
    IMAGE_DIRECTORY = "C:\Users\jiml\Dropbox\#AIArt\SourceCode\CODE_CLIP_Analysis\Images"  # Replace with your image directory
    process_images(IMAGE_DIRECTORY)