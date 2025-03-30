import asyncio
from vtstudio.client import VTubeStudioClient

# Callback function to handle unsolicited events from VTube Studio.
async def handle_events(event):
    # Print the event type and its data.
    print(f"[Event] {event.get('messageType')}: {event.get('data')}")

# Demonstrate UDP discovery: This function listens for UDP broadcast messages
# from VTube Studio (which are sent on port 47779) and prints any messages found.
async def demo_udp_discovery(client):
    print("\n--- UDP Discovery ---")
    discovered = await client.udp_discover(timeout=5.0)
    if discovered:
        for addr, message in discovered:
            print(f"From {addr}: {message}")
    else:
        print("No UDP broadcasts discovered.")

# Demonstrate API state: Query the current API state from VTube Studio.
async def demo_api_state(client):
    print("\n--- API State ---")
    state = await client.get_api_state()
    print("API State:", state)

# Demonstrate retrieving available models: This function calls the API to get a list
# of available models, prints their names and IDs, and returns the list.
async def demo_models(client):
    print("\n--- Getting Available Models ---")
    models_resp = await client.get_models()
    models = models_resp.get("data", {}).get("availableModels", [])
    if models:
        for model in models:
            print(f"Model: {model.get('modelName')} (ID: {model.get('modelID')})")
    else:
        print("No models available.")
    return models

# Demonstrate loading a model: Loads the model with the given ID and prints the response.
async def demo_load_model(client, model_id):
    print(f"\n--- Loading Model {model_id} ---")
    load_resp = await client.load_model(model_id)
    print("Load Model Response:", load_resp)

# Demonstrate parameter control and expression state: This sets a parameter (for example, "ParamMouthOpen")
# and then retrieves the current expression state.
async def demo_parameters(client):
    print("\n--- Setting Parameter and Getting Expression State ---")
    set_param_resp = await client.set_parameter("ParamMouthOpen", 1.0)
    print("Set Parameter Response:", set_param_resp)
    expr_state = await client.get_expression_state()
    print("Expression State:", expr_state)

# Demonstrate moving the model: This function moves the model to a new position, rotation, and scale.
async def demo_movement(client):
    print("\n--- Moving the Model ---")
    move_resp = await client.move_model(position_x=0.1, position_y=-0.1, rotation=5, scale_x=1.0, scale_y=1.0)
    print("Move Model Response:", move_resp)

# Demonstrate face tracking: Retrieves and prints the face tracking data.
async def demo_face_tracking(client):
    print("\n--- Getting Face Tracking Data ---")
    face_data = await client.get_face_tracking_data()
    print("Face Tracking Data:", face_data)

# Demonstrate hotkey retrieval: This function fetches and prints the list of hotkeys.
async def demo_hotkeys(client):
    print("\n--- Getting Hotkeys ---")
    hotkeys_resp = await client.get_hotkeys()
    print("Hotkeys Response:", hotkeys_resp)

# Demonstrate art mesh list retrieval: This function retrieves and prints the list of ArtMeshes.
async def demo_artmeshes(client):
    print("\n--- Getting ArtMesh List ---")
    artmesh_resp = await client.get_artmesh_list()
    print("ArtMesh List:", artmesh_resp)

# Demonstrate statistics: Retrieves and prints current statistics from VTube Studio.
async def demo_statistics(client):
    print("\n--- Getting Statistics ---")
    stats = await client.get_statistics()
    print("Statistics:", stats)

# Demonstrate retrieving folder info: Retrieves and prints folder info (models, backgrounds, etc.).
async def demo_vts_folder_info(client):
    print("\n--- Getting VTS Folder Info ---")
    folder_info = await client.get_vts_folder_info()
    print("VTS Folder Info:", folder_info)

# Demonstrate input parameter list retrieval.
async def demo_input_parameters(client):
    print("\n--- Getting Input Parameter List ---")
    params = await client.get_input_parameter_list()
    print("Input Parameters:", params)

# Demonstrate Live2D parameter list retrieval.
async def demo_live2d_parameters(client):
    print("\n--- Getting Live2D Parameter List ---")
    live2d_params = await client.get_live2d_parameter_list()
    print("Live2D Parameters:", live2d_params)

# Main function demonstrating usage of the client.
async def main():
    # Initialize the client with custom values if desired.
    client = VTubeStudioClient(uri="ws://0.0.0.0:8001",
                               plugin_name="VTubeBridge",
                               plugin_developer="Araxyso Aka (Zinny)")
    await client.connect()

    # Subscribe to events and start the event listener in the background.
    sub_resp = await client.subscribe_to_events(["ModelLoadedEvent", "TrackingStatusChangedEvent"])
    print("Event Subscription Response:", sub_resp)
    asyncio.create_task(client.listen_for_events(handle_events))

    # Demonstrate UDP discovery.
    await demo_udp_discovery(client)

    # Demonstrate API state request.
    await demo_api_state(client)

    # Retrieve available models and, if available, load the first model.
    models = await demo_models(client)
    if models:
        await demo_load_model(client, models[0].get("modelID"))

    # Demonstrate parameter control and model movement.
    await demo_parameters(client)
    await demo_movement(client)

    # Demonstrate getting face tracking data.
    await demo_face_tracking(client)

    # Demonstrate retrieving hotkeys and artmesh list.
    await demo_hotkeys(client)
    await demo_artmeshes(client)

    # Demonstrate retrieving statistics, folder info, and parameter lists.
    await demo_statistics(client)
    await demo_vts_folder_info(client)
    await demo_input_parameters(client)
    await demo_live2d_parameters(client)

    # Keep running for a while to allow events to be processed.
    await asyncio.sleep(10)

    # Gracefully disconnect.
    await client.disconnect()
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())