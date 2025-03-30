# vtstudio

**vtstudio** is a full-featured Python wrapper for the [VTube Studio API](https://github.com/DenchiSoft/VTubeStudio). It supports real-time event handling, model/item control, expression monitoring, hotkey triggering, and more.

## Features

- **WebSocket-based async communication:** Seamlessly interact with the VTube Studio API.
- **Model, Item, and Background Management:** Load models, control items, and adjust backgrounds.
- **Transformations:** Scale, rotate, and move models and items.
- **Parameter Control:** Inject parameter values.
- **Hotkey and Expression Triggers:** Activate hotkeys and trigger expressions.
- **Event Subscription:** Subscribe to and handle VTube Studio events in real time.
- **ArtMesh Opacity Control and Animation Triggering:** Adjust art mesh properties and play animations.

## CLI Usage

Use the following commands to interact with VTube Studio via the CLI:

```bash
python -m vtstudio list-models
python -m vtstudio load-model --id MODEL_ID
python -m vtstudio trigger-hotkey --id HOTKEY_ID
python -m vtstudio trigger-expression --file EXPRESSION_FILE
python -m vtstudio set-param --name ParamName --value 1.0
python -m vtstudio scale-model --posx 0 --posy 0 --rotation 0 --scalex 1.0 --scaley 1.0
python -m vtstudio rotate-scale-item --instance 1001 --rotation 45 --scalex 1.2 --scaley 1.2
python -m vtstudio face-tracking
python -m vtstudio get-expression
python -m vtstudio set-artmesh-opacity --tag ArtMeshTag --opacity 0.5
python -m vtstudio trigger-animation --file animation.motion3.json
```

Example

To run the example script, use:
```bash
python examples/main.py
```

Installation

Clone the repository and install the necessary dependencies:
```bash
pip install websockets colorama
```

License

This project is licensed under the MIT License.