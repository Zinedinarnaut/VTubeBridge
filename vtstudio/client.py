import asyncio
import websockets
import json
import uuid

# UDP Discovery Protocol to collect broadcast messages from VTube Studio.
class UDPDiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.messages = []
    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode("utf-8"))
            self.messages.append((addr, message))
        except Exception:
            pass

class VTubeStudioClient:
    def __init__(self, uri="ws://0.0.0.0:8001", plugin_name="VTubeBridge", plugin_developer="Araxyso Aka (Zinny)"):
        self.uri = uri
        self.token = None
        self.websocket = None
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        # For handling responses:
        self.pending_requests = {}  # Maps requestID to asyncio.Future
        self.event_queue = asyncio.Queue()  # For unsolicited events
        self._listener_task = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        # Start a single listener loop that handles all incoming messages.
        self._listener_task = asyncio.create_task(self._listener_loop())
        await self.authenticate()

    async def _listener_loop(self):
        """Continuously read messages from the websocket and dispatch them."""
        while True:
            try:
                msg_str = await self.websocket.recv()
            except Exception as e:
                # Handle disconnection if needed.
                break
            try:
                msg = json.loads(msg_str)
            except Exception:
                continue
            req_id = msg.get("requestID")
            if req_id and req_id in self.pending_requests:
                fut = self.pending_requests.pop(req_id)
                if not fut.done():
                    fut.set_result(msg)
            else:
                # Unsolicited event – put it in the event queue.
                await self.event_queue.put(msg)

    async def send_request(self, request: dict):
        """
        Helper method: creates a Future for this request,
        sends it, and waits for the corresponding response.
        """
        req_id = request.get("requestID", str(uuid.uuid4()))
        request["requestID"] = req_id
        fut = asyncio.get_event_loop().create_future()
        self.pending_requests[req_id] = fut
        await self.send(request)
        return await fut

    async def send(self, message: dict):
        await self.websocket.send(json.dumps(message))

    async def receive(self):
        """Direct receive (not used by API methods)"""
        return json.loads(await self.websocket.recv())

    async def authenticate(self):
        # If we don't already have a token, request one.
        if not self.token:
            token_request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": str(uuid.uuid4()),
                "messageType": "AuthenticationTokenRequest",
                "data": {
                    "pluginName": self.plugin_name,
                    "pluginDeveloper": self.plugin_developer,
                    "pluginIcon": ""  # Optionally, a base64-encoded 128x128 PNG/JPG.
                }
            }
            token_response = await self.send_request(token_request)
            print("Token response:", token_response)
            if token_response.get("messageType") == "APIError":
                print("Error requesting token:", token_response.get("data", {}).get("message"))
                return token_response
            self.token = token_response["data"].get("authenticationToken", "")
            if not self.token:
                print("Failed to obtain an authentication token.")
                return token_response

        # Now authenticate using the token.
        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "authenticationToken": self.token
            }
        }
        auth_response = await self.send_request(auth_request)
        print("Authentication response:", auth_response)
        if auth_response.get("messageType") == "APIError":
            print("Authentication error:", auth_response.get("data", {}).get("message"))
        return auth_response

    # ----- Basic API Methods -----

    async def get_models(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "AvailableModelsRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def load_model(self, model_id):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "LoadModelRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"modelID": model_id}
        }
        return await self.send_request(request)

    async def trigger_hotkey(self, hotkey_id):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "HotkeyTriggerRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"hotkeyID": hotkey_id}
        }
        return await self.send_request(request)

    async def set_parameter(self, name, value):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "InjectParameterDataRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"parameterValues": [{"id": name, "value": value}]}
        }
        return await self.send_request(request)

    async def subscribe_to_events(self, events):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "EventSubscriptionRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"subscribeTo": events}
        }
        return await self.send_request(request)

    async def listen_for_events(self, callback):
        """Continuously get unsolicited events and invoke the callback."""
        while True:
            event = await self.event_queue.get()
            await callback(event)

    async def scale_item(self, instance_id, scale_x, scale_y):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "MoveLive2DItemRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"instanceID": instance_id, "scaleX": scale_x, "scaleY": scale_y, "timeInSeconds": 0.5}
        }
        return await self.send_request(request)

    async def rotate_item(self, instance_id, rotation):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "MoveLive2DItemRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"instanceID": instance_id, "rotation": rotation, "timeInSeconds": 0.5}
        }
        return await self.send_request(request)

    async def get_expression_state(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ExpressionStateRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def toggle_expression(self, expression_file: str, active: bool = True, fade_time: float = 0.5):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "ExpressionActivationRequest",
            "data": {"expressionFile": expression_file, "fadeTime": fade_time, "active": active}
        }
        return await self.send_request(request)

    async def move_model(self, position_x=0.0, position_y=0.0, rotation=0.0, scale_x=1.0, scale_y=1.0):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "MoveModelRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"positionX": position_x, "positionY": position_y, "rotation": rotation, "scaleX": scale_x, "scaleY": scale_y, "timeInSeconds": 0.5}
        }
        return await self.send_request(request)

    async def rotate_and_scale_item(self, instance_id, rotation, scale_x, scale_y):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "MoveLive2DItemRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"instanceID": instance_id, "rotation": rotation, "scaleX": scale_x, "scaleY": scale_y, "timeInSeconds": 0.5}
        }
        return await self.send_request(request)

    async def get_face_tracking_data(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "FaceFoundRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def set_artmesh_opacity(self, tag_exact: str, opacity: float):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ColorTintRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "artMeshMatcher": {"tintAll": False, "tagExact": tag_exact},
                "colorTint": {"colorR": 1.0, "colorG": 1.0, "colorB": 1.0, "colorA": opacity},
                "blendToOriginalTime": 0.5,
                "blendMode": 0
            }
        }
        return await self.send_request(request)

    async def trigger_animation(self, animation_file: str):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "PlayAnimationRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"animationFileName": animation_file}
        }
        return await self.send_request(request)

    # ----- Additional VTube Studio Features -----

    async def get_current_model(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "CurrentModelRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_hotkeys(self, model_id: str = "", live2dItemFileName: str = ""):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "HotkeysInCurrentModelRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"modelID": model_id, "live2DItemFileName": live2dItemFileName}
        }
        return await self.send_request(request)

    async def get_artmesh_list(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ArtMeshListRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_statistics(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "StatisticsRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_vts_folder_info(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "VTSFolderInfoRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_input_parameter_list(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "InputParameterListRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_live2d_parameter_list(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "Live2DParameterListRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def get_parameter_value(self, name: str):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ParameterValueRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"name": name}
        }
        return await self.send_request(request)

    async def create_parameter(self, parameter_name: str, explanation: str, min_val: float, max_val: float, default_value: float):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ParameterCreationRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "parameterName": parameter_name,
                "explanation": explanation,
                "min": min_val,
                "max": max_val,
                "defaultValue": default_value
            }
        }
        return await self.send_request(request)

    async def delete_parameter(self, parameter_name: str):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ParameterDeletionRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"parameterName": parameter_name}
        }
        return await self.send_request(request)

    async def get_current_model_physics(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "GetCurrentModelPhysicsRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def set_current_model_physics(self, strength_overrides: list, wind_overrides: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "SetCurrentModelPhysicsRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"strengthOverrides": strength_overrides, "windOverrides": wind_overrides}
        }
        return await self.send_request(request)

    async def ndi_config(self, setNewConfig: bool, ndiActive: bool, useNDI5: bool, useCustomResolution: bool, customWidthNDI: int, customHeightNDI: int):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "NDIConfigRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "setNewConfig": setNewConfig,
                "ndiActive": ndiActive,
                "useNDI5": useNDI5,
                "useCustomResolution": useCustomResolution,
                "customWidthNDI": customWidthNDI,
                "customHeightNDI": customHeightNDI
            }
        }
        return await self.send_request(request)

    async def item_list(self, includeAvailableSpots: bool, includeItemInstancesInScene: bool, includeAvailableItemFiles: bool, onlyItemsWithFileName: str = "", onlyItemsWithInstanceID: str = ""):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemListRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "includeAvailableSpots": includeAvailableSpots,
                "includeItemInstancesInScene": includeItemInstancesInScene,
                "includeAvailableItemFiles": includeAvailableItemFiles,
                "onlyItemsWithFileName": onlyItemsWithFileName,
                "onlyItemsWithInstanceID": onlyItemsWithInstanceID
            }
        }
        return await self.send_request(request)

    async def item_load(self, fileName: str, positionX: float, positionY: float, size: float, rotation: float, fadeTime: float, order: int, failIfOrderTaken: bool, smoothing: float, censored: bool, flipped: bool, locked: bool, unloadWhenPluginDisconnects: bool, customDataBase64: str = "", customDataAskUserFirst: bool = False, customDataSkipAskingUserIfWhitelisted: bool = True, customDataAskTimer: float = -1):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemLoadRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "fileName": fileName,
                "positionX": positionX,
                "positionY": positionY,
                "size": size,
                "rotation": rotation,
                "fadeTime": fadeTime,
                "order": order,
                "failIfOrderTaken": failIfOrderTaken,
                "smoothing": smoothing,
                "censored": censored,
                "flipped": flipped,
                "locked": locked,
                "unloadWhenPluginDisconnects": unloadWhenPluginDisconnects,
                "customDataBase64": customDataBase64,
                "customDataAskUserFirst": customDataAskUserFirst,
                "customDataSkipAskingUserIfWhitelisted": customDataSkipAskingUserIfWhitelisted,
                "customDataAskTimer": customDataAskTimer
            }
        }
        return await self.send_request(request)

    async def item_unload(self, unloadAllInScene: bool, unloadAllLoadedByThisPlugin: bool, allowUnloadingItemsLoadedByUserOrOtherPlugins: bool, instanceIDs: list, fileNames: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemUnloadRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "unloadAllInScene": unloadAllInScene,
                "unloadAllLoadedByThisPlugin": unloadAllLoadedByThisPlugin,
                "allowUnloadingItemsLoadedByUserOrOtherPlugins": allowUnloadingItemsLoadedByUserOrOtherPlugins,
                "instanceIDs": instanceIDs,
                "fileNames": fileNames
            }
        }
        return await self.send_request(request)

    async def item_animation_control(self, itemInstanceID: str, framerate: float, frame: int, brightness: float, opacity: float, setAutoStopFrames: bool, autoStopFrames: list, setAnimationPlayState: bool, animationPlayState: bool):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemAnimationControlRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "itemInstanceID": itemInstanceID,
                "framerate": framerate,
                "frame": frame,
                "brightness": brightness,
                "opacity": opacity,
                "setAutoStopFrames": setAutoStopFrames,
                "autoStopFrames": autoStopFrames,
                "setAnimationPlayState": setAnimationPlayState,
                "animationPlayState": animationPlayState
            }
        }
        return await self.send_request(request)

    async def item_move(self, itemsToMove: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemMoveRequest",
            "requestID": str(uuid.uuid4()),
            "data": {"itemsToMove": itemsToMove}
        }
        return await self.send_request(request)

    async def artmesh_selection(self, textOverride: str, helpOverride: str, requestedArtMeshCount: int, activeArtMeshes: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ArtMeshSelectionRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "textOverride": textOverride,
                "helpOverride": helpOverride,
                "requestedArtMeshCount": requestedArtMeshCount,
                "activeArtMeshes": activeArtMeshes
            }
        }
        return await self.send_request(request)

    async def item_pin(self, pin: bool, itemInstanceID: str, angleRelativeTo: str, sizeRelativeTo: str, vertexPinType: str, pinInfo: dict):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ItemPinRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "pin": pin,
                "itemInstanceID": itemInstanceID,
                "angleRelativeTo": angleRelativeTo,
                "sizeRelativeTo": sizeRelativeTo,
                "vertexPinType": vertexPinType,
                "pinInfo": pinInfo
            }
        }
        return await self.send_request(request)

    async def post_processing_list(self, fillPostProcessingPresetsArray: bool, fillPostProcessingEffectsArray: bool, effectIDFilter: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "PostProcessingListRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "fillPostProcessingPresetsArray": fillPostProcessingPresetsArray,
                "fillPostProcessingEffectsArray": fillPostProcessingEffectsArray,
                "effectIDFilter": effectIDFilter
            }
        }
        return await self.send_request(request)

    async def post_processing_update(self, postProcessingOn: bool, setPostProcessingPreset: bool, setPostProcessingValues: bool, presetToSet: str, postProcessingFadeTime: float, setAllOtherValuesToDefault: bool, usingRestrictedEffects: bool, randomizeAll: bool, randomizeAllChaosLevel: float, postProcessingValues: list):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "PostProcessingUpdateRequest",
            "requestID": str(uuid.uuid4()),
            "data": {
                "postProcessingOn": postProcessingOn,
                "setPostProcessingPreset": setPostProcessingPreset,
                "setPostProcessingValues": setPostProcessingValues,
                "presetToSet": presetToSet,
                "postProcessingFadeTime": postProcessingFadeTime,
                "setAllOtherValuesToDefault": setAllOtherValuesToDefault,
                "usingRestrictedEffects": usingRestrictedEffects,
                "randomizeAll": randomizeAll,
                "randomizeAllChaosLevel": randomizeAllChaosLevel,
                "postProcessingValues": postProcessingValues
            }
        }
        return await self.send_request(request)

    # ----- Additional Utility Methods -----

    async def get_api_state(self):
        """Request the current API state from VTube Studio."""
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "APIStateRequest",
            "requestID": str(uuid.uuid4())
        }
        return await self.send_request(request)

    async def disconnect(self):
        """Gracefully disconnect from the VTube Studio API."""
        if self._listener_task:
            self._listener_task.cancel()
        if self.websocket:
            await self.websocket.close()

    async def udp_discover(self, timeout: float = 5.0):
        """
        Discover VTube Studio UDP broadcasts on port 47779.
        Returns a list of tuples: (address, message)
        """
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPDiscoveryProtocol(), local_addr=("0.0.0.0", 47779)
        )
        await asyncio.sleep(timeout)
        transport.close()
        return protocol.messages