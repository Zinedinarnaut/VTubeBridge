# VTubeBridge

**VTubeBridge** is a full-featured Python wrapper for the [VTube Studio API](https://github.com/DenchiSoft/VTubeStudio). It allows you to seamlessly interact with VTube Studio using asynchronous WebSocket communication and supports nearly all API endpoints.

## Features

- **Async WebSocket Communication:**  
  Interact with VTube Studio’s API in real time using asynchronous requests.

- **Model, Item, and Background Management:**  
  - Load and unload models  
  - Manage items (load, unload, move, animate, pin)  
  - Adjust backgrounds

- **Transformations & Parameter Control:**  
  - Scale, rotate, and move models and items  
  - Inject and modify Live2D parameters

- **Hotkey & Expression Triggers:**  
  Trigger hotkeys (which control expressions, animations, etc.) via the API.

- **Event Subscription:**  
  Subscribe to and handle VTube Studio events (e.g., model load, tracking changes) in real time.

- **ArtMesh Control:**  
  Adjust art mesh properties (such as opacity) and trigger animations.

- **Advanced API Operations:**  
  - Query API state  
  - Retrieve statistics and folder information  
  - Access both default and custom input parameter lists

- **Physics & NDI Control:**  
  - Get and override physics settings for the current model  
  - Configure NDI streaming settings

- **UDP Server Discovery:**  
  Discover VTube Studio instances on your network via UDP broadcasts.

- **Graceful Disconnection:**  
  Cleanly disconnect from the API when your application is done.

## CLI Usage

You can also interact with VTube Studio using the provided command-line interface. For example:

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