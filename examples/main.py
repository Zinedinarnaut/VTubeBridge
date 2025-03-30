import asyncio
from vtstudio.client import VTubeStudioClient


async def handle_events(event):
    print(f"[Event] {event.get('messageType')}: {event.get('data')}")


async def demo_udp_discovery(client):
    print("\n--- UDP Discovery ---")
    discovered = await client.udp_discover(timeout=5.0)
    if discovered:
        for addr, message in discovered:
            print(f"From {addr}: {message}")
    else:
        print("No UDP broadcasts discovered.")


async def demo_api_state(client):
    print("\n--- API State ---")
    state = await client.get_api_state()
    print("API State:", state)


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


async def demo_load_model(client, model_id):
    print(f"\n--- Loading Model {model_id} ---")
    load_resp = await client.load_model(model_id)
    print("Load Model Response:", load_resp)


async def demo_parameters(client):
    print("\n--- Setting Parameter and Getting Expression State ---")
    set_param_resp = await client.set_parameter("ParamMouthOpen", 1.0)
    print("Set Parameter Response:", set_param_resp)
    expr_state = await client.get_expression_state()
    print("Expression State:", expr_state)


async def demo_movement(client):
    print("\n--- Moving the Model ---")
    move_resp = await client.move_model(position_x=0.1, position_y=-0.1, rotation=5, scale_x=1.0, scale_y=1.0)
    print("Move Model Response:", move_resp)


async def demo_face_tracking(client):
    print("\n--- Getting Face Tracking Data ---")
    face_data = await client.get_face_tracking_data()
    print("Face Tracking Data:", face_data)


async def demo_hotkeys(client):
    print("\n--- Getting Hotkeys ---")
    hotkeys_resp = await client.get_hotkeys()
    print("Hotkeys Response:", hotkeys_resp)


async def demo_artmeshes(client):
    print("\n--- Getting ArtMesh List ---")
    artmesh_resp = await client.get_artmesh_list()
    print("ArtMesh List:", artmesh_resp)


async def demo_statistics(client):
    print("\n--- Getting Statistics ---")
    stats = await client.get_statistics()
    print("Statistics:", stats)


async def demo_vts_folder_info(client):
    print("\n--- Getting VTS Folder Info ---")
    folder_info = await client.get_vts_folder_info()
    print("VTS Folder Info:", folder_info)


async def demo_input_parameters(client):
    print("\n--- Getting Input Parameter List ---")
    params = await client.get_input_parameter_list()
    print("Input Parameters:", params)


async def demo_live2d_parameters(client):
    print("\n--- Getting Live2D Parameter List ---")
    live2d_params = await client.get_live2d_parameter_list()
    print("Live2D Parameters:", live2d_params)


async def main():
    client = VTubeStudioClient()
    await client.connect()

    # Subscribe to events and start the event listener in background.
    sub_resp = await client.subscribe_to_events(["ModelLoadedEvent", "TrackingStatusChangedEvent"])
    print("Event Subscription Response:", sub_resp)
    asyncio.create_task(client.listen_for_events(handle_events))

    # Demonstrate UDP discovery.
    await demo_udp_discovery(client)

    # Demonstrate API state request.
    await demo_api_state(client)

    # Get available models and load the first one if available.
    models = await demo_models(client)
    if models:
        await demo_load_model(client, models[0].get("modelID"))

    # Demonstrate setting parameters and moving the model.
    await demo_parameters(client)
    await demo_movement(client)

    # Demonstrate getting face tracking data.
    await demo_face_tracking(client)

    # Demonstrate getting hotkeys and artmesh list.
    await demo_hotkeys(client)
    await demo_artmeshes(client)

    # Demonstrate getting statistics, folder info, and parameter lists.
    await demo_statistics(client)
    await demo_vts_folder_info(client)
    await demo_input_parameters(client)
    await demo_live2d_parameters(client)

    # Keep running for a while to receive events.
    await asyncio.sleep(10)

    # Gracefully disconnect.
    await client.disconnect()
    print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())