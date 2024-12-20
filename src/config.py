import os
import sys
import json
from termcolor import colored

ROOT_DIR = os.path.dirname(sys.path[0])

def error(message: str, show_emoji: bool = True) -> None:
    emoji = "[ERROR]" if show_emoji else ""
    print(colored(f"{emoji} {message}", "white"))

def info(message: str, show_emoji: bool = True) -> None:
    emoji = "[INFO]" if show_emoji else ""
    print(colored(f"{emoji} {message}", "white"))

def warning(message: str, show_emoji: bool = True) -> None:
    emoji = "[INFO]" if show_emoji else ""
    print(colored(f"{emoji} {message}", "green"))

def get_fonts_dir() -> str:
    return os.path.join(ROOT_DIR, "fonts")

def get_music_dir() -> str:
    return os.path.join(ROOT_DIR, "music")

def assert_folder_structure() -> None:
    if not os.path.exists(os.path.join(ROOT_DIR, ".mp")):
        if get_verbose():
            print(colored(f"Creating .mp folder at {os.path.join(ROOT_DIR, '.mp')}", "green"))
        os.makedirs(os.path.join(ROOT_DIR, ".mp"))

def get_threads() -> int:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["threads"]

def get_subtitles() -> bool:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["subtitles"]

def get_dimension() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["dimension"]

def get_highlight() -> bool:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["highlight"]

def get_assemblyai_api_key() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["assembly_ai_api_key"]

def get_font() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["font"]

def get_imagemagick_path() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["imagemagick_path"]

def get_effect() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["effect"]

def get_max_duration() -> float:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["max_duration"]

def get_max_chars() -> int:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["max_chars"]

def get_max_lines() -> int:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["max_lines"]

def get_max_gap() -> float:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["max_gap"]

def get_font_size() -> int:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["font_size"]

def get_subtitle_color() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["subtitle_color"]

def get_highlight_color() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["highlight_color"]

def get_stroke_color() -> str:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["stroke_color"]

def get_stroke_width() -> int:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return json.load(file)["stroke_width"]
