"""
MP Aspect Latent Picker
-----------------------
A general-purpose empty-latent node for ComfyUI.

Two sizing methods (chosen by 'sizing_mode'; the irrelevant field is hidden by the
companion JS extension):
  - "megapixels":        aspect ratio + a megapixel budget -> dimensions are solved for you.
  - "scale from preset": take the preset (or a custom pixel size) and multiply by a factor.

The aspect dropdown lists both landscape and portrait resolutions with their ratios.
For an uncommon resolution, set width_override AND height_override directly in pixels.

Dimensions are rounded to a multiple of 8 (standard VAE requirement).

Outputs a standard ComfyUI LATENT (classic 4-channel empty latent; works across
SD1.x / SD2 / SDXL / SD3 / Flux) plus the resolved width and height as INT.
"""

import math
import torch


# Dimensions are rounded to a multiple of this (VAE downscale factor).
DIVISIBLE_BY = 8

# Full preset list, landscape and portrait, value = (width, height).
ASPECT_PRESETS = {
    "704 x 1408 (0.5)": (704, 1408),
    "704 x 1344 (0.52)": (704, 1344),
    "768 x 1344 (0.57)": (768, 1344),
    "768 x 1280 (0.6)": (768, 1280),
    "832 x 1216 (0.68)": (832, 1216),
    "832 x 1152 (0.72)": (832, 1152),
    "896 x 1152 (0.78)": (896, 1152),
    "896 x 1088 (0.82)": (896, 1088),
    "960 x 1088 (0.88)": (960, 1088),
    "960 x 1024 (0.94)": (960, 1024),
    "1024 x 1024 (1.0)": (1024, 1024),
    "1024 x 960 (1.07)": (1024, 960),
    "1088 x 960 (1.13)": (1088, 960),
    "1088 x 896 (1.21)": (1088, 896),
    "1152 x 896 (1.29)": (1152, 896),
    "1152 x 832 (1.38)": (1152, 832),
    "1216 x 832 (1.46)": (1216, 832),
    "1280 x 768 (1.67)": (1280, 768),
    "1344 x 768 (1.75)": (1344, 768),
    "1344 x 704 (1.91)": (1344, 704),
    "1408 x 704 (2.0)": (1408, 704),
    "1472 x 704 (2.09)": (1472, 704),
    "1536 x 640 (2.4)": (1536, 640),
    "1600 x 640 (2.5)": (1600, 640),
    "1664 x 576 (2.89)": (1664, 576),
    "1728 x 576 (3.0)": (1728, 576),
}


def _round_to(value, multiple):
    multiple = max(1, int(multiple))
    return max(multiple, int(round(value / multiple)) * multiple)


class MPAspectLatentPicker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sizing_mode": (["megapixels", "scale from preset"], {
                    "tooltip": "Which method drives the size. The unused field below is hidden."}),
                "aspect_ratio": (list(ASPECT_PRESETS.keys()), {
                    "default": "1024 x 1024 (1.0)",
                    "tooltip": "Base resolution (landscape or portrait). Ignored if both "
                               "width_override and height_override are set."}),
                # Only one of the next two is visible at a time (handled by the JS extension).
                "megapixels": ("FLOAT", {
                    "default": 1.0, "min": 0.01, "max": 256.0, "step": 0.05,
                    "tooltip": "Target pixel budget in millions. Used in 'megapixels' mode."}),
                "scale": ("FLOAT", {
                    "default": 1.0, "min": 0.05, "max": 16.0, "step": 0.05,
                    "tooltip": "Linear multiplier on the base resolution. Used in 'scale from preset' mode."}),
                "width_override": ("INT", {
                    "default": 0, "min": 0, "max": 16384, "step": 1,
                    "tooltip": "Custom base width in pixels. Set this AND height_override to use an "
                               "exact uncommon resolution instead of the preset. 0 = use preset."}),
                "height_override": ("INT", {
                    "default": 0, "min": 0, "max": 16384, "step": 1,
                    "tooltip": "Custom base height in pixels. Set this AND width_override. 0 = use preset."}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("LATENT", "width", "height")
    FUNCTION = "generate"
    CATEGORY = "latent"

    def generate(self, sizing_mode, aspect_ratio, megapixels, scale,
                 width_override, height_override, batch_size):
        # Base resolution: preset, unless both pixel overrides are set.
        if width_override > 0 and height_override > 0:
            base_w, base_h = width_override, height_override
        else:
            base_w, base_h = ASPECT_PRESETS[aspect_ratio]
        ratio = base_w / base_h

        if sizing_mode == "megapixels":
            pixels = max(1.0, megapixels * 1_000_000.0)
            height = math.sqrt(pixels / ratio)
            width = ratio * height
        else:  # scale from preset
            width = base_w * scale
            height = base_h * scale

        width = _round_to(width, DIVISIBLE_BY)
        height = _round_to(height, DIVISIBLE_BY)

        # Classic ComfyUI empty latent (4 channels, /8 spatial). Broadly compatible.
        latent = torch.zeros([batch_size, 4, height // 8, width // 8])

        print(f"[MPAspectLatentPicker] {width}x{height} "
              f"(ratio {width / height:.3f}, {width * height / 1_000_000.0:.2f} MP, "
              f"batch {batch_size}, mode={sizing_mode})")

        return ({"samples": latent}, width, height)


NODE_CLASS_MAPPINGS = {"MPAspectLatentPicker": MPAspectLatentPicker}
NODE_DISPLAY_NAME_MAPPINGS = {"MPAspectLatentPicker": "MP Aspect Latent Picker"}
