import asyncio
import argparse
from client import VTubeStudioClient
from colorama import init, Fore, Style

init(autoreset=True)

async def main():
    parser = argparse.ArgumentParser(description="VTube Studio CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Base commands
    subparsers.add_parser("list-models", help="List all available models")

    load_model_parser = subparsers.add_parser("load-model", help="Load a model by ID")
    load_model_parser.add_argument("--id", required=True, help="Model ID to load")

    hotkey_parser = subparsers.add_parser("trigger-hotkey", help="Trigger a hotkey")
    hotkey_parser.add_argument("--id", required=True, help="Hotkey ID to trigger")

    expression_parser = subparsers.add_parser("trigger-expression", help="Trigger an expression")
    expression_parser.add_argument("--file", required=True, help="Expression file name")

    # Additional commands
    set_param_parser = subparsers.add_parser("set-param", help="Set a parameter value")
    set_param_parser.add_argument("--name", required=True, help="Parameter name")
    set_param_parser.add_argument("--value", required=True, type=float, help="Parameter value")

    scale_model_parser = subparsers.add_parser("scale-model", help="Move, rotate, and scale the model")
    scale_model_parser.add_argument("--posx", type=float, default=0.0, help="X position")
    scale_model_parser.add_argument("--posy", type=float, default=0.0, help="Y position")
    scale_model_parser.add_argument("--rotation", type=float, default=0.0, help="Rotation angle")
    scale_model_parser.add_argument("--scalex", type=float, default=1.0, help="Scale X")
    scale_model_parser.add_argument("--scaley", type=float, default=1.0, help="Scale Y")

    rotate_scale_item_parser = subparsers.add_parser("rotate-scale-item", help="Rotate and scale an item")
    rotate_scale_item_parser.add_argument("--instance", required=True, type=int, help="Item instance ID")
    rotate_scale_item_parser.add_argument("--rotation", type=float, required=True, help="Rotation angle")
    rotate_scale_item_parser.add_argument("--scalex", type=float, required=True, help="Scale X")
    rotate_scale_item_parser.add_argument("--scaley", type=float, required=True, help="Scale Y")

    face_tracking_parser = subparsers.add_parser("face-tracking", help="Get face tracking data")

    get_expression_parser = subparsers.add_parser("get-expression", help="Get expression state")

    artmesh_opacity_parser = subparsers.add_parser("set-artmesh-opacity", help="Set artmesh opacity")
    artmesh_opacity_parser.add_argument("--tag", required=True, help="ArtMesh tag")
    artmesh_opacity_parser.add_argument("--opacity", required=True, type=float, help="Opacity value (0.0 to 1.0)")

    trigger_animation_parser = subparsers.add_parser("trigger-animation", help="Trigger an animation")
    trigger_animation_parser.add_argument("--file", required=True, help="Animation file name")

    args = parser.parse_args()
    vts = VTubeStudioClient()
    await vts.connect()

    if args.command == "list-models":
        models = await vts.get_models()
        for model in models["data"]["availableModels"]:
            print(f"{Fore.GREEN}{model['modelID']}{Style.RESET_ALL}: {model['modelName']}")
    elif args.command == "load-model":
        response = await vts.load_model(args.id)
        print(f"{Fore.GREEN}Model Load Response:{Style.RESET_ALL} {response}")
    elif args.command == "trigger-hotkey":
        response = await vts.trigger_hotkey(args.id)
        print(f"{Fore.GREEN}Hotkey Triggered:{Style.RESET_ALL} {response}")
    elif args.command == "trigger-expression":
        response = await vts.trigger_expression(args.file)
        print(f"{Fore.GREEN}Expression Triggered:{Style.RESET_ALL} {response}")
    elif args.command == "set-param":
        response = await vts.set_parameter(args.name, args.value)
        print(f"{Fore.GREEN}Parameter Set:{Style.RESET_ALL} {response}")
    elif args.command == "scale-model":
        response = await vts.move_model(
            position_x=args.posx,
            position_y=args.posy,
            rotation=args.rotation,
            scale_x=args.scalex,
            scale_y=args.scaley
        )
        print(f"{Fore.GREEN}Model Scaled/Rotated/Moved:{Style.RESET_ALL} {response}")
    elif args.command == "rotate-scale-item":
        response = await vts.rotate_and_scale_item(
            args.instance,
            args.rotation,
            args.scalex,
            args.scaley
        )
        print(f"{Fore.GREEN}Item Rotated/Scaled:{Style.RESET_ALL} {response}")
    elif args.command == "face-tracking":
        response = await vts.get_face_tracking_data()
        print(f"{Fore.GREEN}Face Tracking Data:{Style.RESET_ALL} {response}")
    elif args.command == "get-expression":
        response = await vts.get_expression_state()
        print(f"{Fore.GREEN}Expression State:{Style.RESET_ALL} {response}")
    elif args.command == "set-artmesh-opacity":
        response = await vts.set_artmesh_opacity(args.tag, args.opacity)
        print(f"{Fore.GREEN}ArtMesh Opacity Set:{Style.RESET_ALL} {response}")
    elif args.command == "trigger-animation":
        response = await vts.trigger_animation(args.file)
        print(f"{Fore.GREEN}Animation Triggered:{Style.RESET_ALL} {response}")
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())