# MP Aspect Latent Picker

A simple ComfyUI custom node designed to streamline latent generation and dimension handling. It outputs an empty LATENT package, alongside matching `width` and `height` integers.

## Features

* **Flexible Sizing Modes:** Switch between preset scaling or target megapixel bounds effortlessly.
* **Aspect Ratio Presets:** Select from common dimensions directly inside the node.
* **Overrides & Batches:** Quickly hardcode specific width/height overrides or adjust the target batch size on the fly.

## Sizing Modes

### 1. Scale From Preset
Scale down or up from your selected base aspect ratio using a simple multiplier.
<img width="798" height="662" alt="image" src="https://github.com/user-attachments/assets/43fcc7bf-6bf7-48cf-8b93-6c4e381dd51c" />


### 2. Megapixels
Automatically calculate and match the aspect ratio dimensions tailored to a target megapixel limit.
<img width="685" height="639" alt="image" src="https://github.com/user-attachments/assets/89c2a637-2c21-4e72-97eb-6b38fbc2a5ef" />

