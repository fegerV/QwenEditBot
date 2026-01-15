# ComfyUI API Usage Guide

This document explains how to use the ComfyUI API with the QwenEdit 2511 workflow.

## Workflow Overview

The QwenEdit 2511 workflow transforms images into comic style while preserving composition and character identity, and removes progress bars and watermarks.

## Prerequisites

Before using the API, ensure:

1. ComfyUI is running on `http://127.0.0.1:8188`
2. The required model files are installed in ComfyUI:
   - `qwen_image_vae.safetensors`
   - `qwen_image_edit_2511_fp8mixed.safetensors`
   - `qwen_2.5_vl_7b_fp8_scaled.safetensors`
   - `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors`
3. The input image file is placed in the ComfyUI input directory (`C:/ComfyUI/ComfyUI/input/bot`)

## API Request Format

The API expects a JSON payload with the following structure:

```json
{
  "prompt": {
    // workflow definition goes here
  }
}
```

## Image File Requirements

The workflow expects an image file named in the format `input_<job_id>_<original_filename>` to be present in the ComfyUI input directory.

In the workflow JSON, the `LoadImage` node (ID 41) specifies the image to load:

```json
"41": {
  "inputs": {
    "image": "input_test.jpg"
  },
  "class_type": "LoadImage",
  "_meta": {
    "title": "Load Image"
  }
}
```

Ensure this field matches the filename of the image you have placed in the ComfyUI input directory.

## Example Request

To send the workflow to ComfyUI:

```bash
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d @path/to/wrapped_workflow.json
```

Where `wrapped_workflow.json` contains the workflow wrapped in the `{"prompt": ...}` structure.

## Error Handling

Common errors:

- `"No prompt provided"`: The JSON was not wrapped in a `{"prompt": ...}` object
- `"Invalid image file"`: The specified image file does not exist in the ComfyUI input directory
- `"Prompt outputs failed validation"`: There was an issue with one or more nodes in the workflow

## Integration with QwenEdit System

For integration with the QwenEdit system, use the worker service, which handles:

1. Copying the uploaded image to the ComfyUI input directory
2. Generating the correct workflow JSON with the appropriate image filename
3. Sending the request to ComfyUI
4. Monitoring the job status
5. Retrieving the result
6. Cleaning up temporary files