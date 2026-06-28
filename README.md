# MP Aspect Latent Picker

A simple ComfyUI custom node designed to streamline latent generation and dimension handling. It outputs an empty LATENT package, alongside matching `width` and `height` integers.

## Features

* **Flexible Sizing Modes:** Switch between preset scaling or target megapixel bounds effortlessly.
* **Aspect Ratio Presets:** Select from common dimensions directly inside the node.
* **Overrides & Batches:** Quickly hardcode specific width/height overrides or adjust the target batch size on the fly.

## Sizing Modes

### 1. Scale From Preset
Scale down or up from your selected base aspect ratio using a simple multiplier.

### 2. Megapixels
Automatically calculate and match the aspect ratio dimensions tailored to a target megapixel limit (e.g., targeting a 4.00 MP generation limit).
