import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

TARGET_URL = os.environ["WEBHOOK_URL"]


@app.post(
    "/zk6785xyJT3A3LenZTBptNLr3IGsv2HeeYmC425ua3WcA4V8agPf6Oqf0PuggovXNmvyFbH2FKGys6WJR0t3K2U9oGUvU94ZgcacDAKbGtrjWTZEJWsV8VGx7JQK929s",
    response_class=JSONResponse,
)
async def webhook_relay(request: Request):
    # Get the incoming JSON data from the request
    data = await request.json()

    # Check if 'challenge' key is present
    if "challenge" in data:
        # Mirror the entire request body back as the response
        return JSONResponse(data, 200)
    else:
        # Forward the request data to the target URL
        try:
            print(data)
            # Translate {'event': {'app': 'monday', 'type': 'create_pulse', 'triggerTime': '2024-12-10T19:27:30.740Z', 'subscriptionId': 444297159, 'userId': 55409066, 'originalTriggerUuid': None, 'boardId': 5992933181, 'pulseId': 8023406464, 'pulseName': 'test', 'groupId': 'new_group', 'groupName': 'Infrastructure', 'groupColor': '#c4c4c4', 'isTopGroup': False, 'columnValues': {}, 'triggerUuid': '4012d98ac0d9229542948fba0464c50d'}}
            # to a discord embed format
            if data["event"]["type"] == "create_pulse":
                webhook_data = {
                    "embeds": [
                        {
                            "title": f"New task in {data['event']['groupName']}",
                            "url": f"https://flowdata.monday.com/boards/{data['event']['boardId']}/pulses/{data['event']['pulseId']}",
                            "description": f"**{data['event']['pulseName']}**",
                            "color": int(data["event"]["groupColor"].lstrip("#"), 16),
                        }
                    ],
                }
            # Translate {'event': {'app': 'monday', 'type': 'update_column_value', 'triggerTime': '2024-12-10T19:37:15.319Z', 'subscriptionId': 444305275, 'userId': 55409066, 'originalTriggerUuid': None, 'boardId': 5992933181, 'groupId': 'new_group', 'pulseId': 8023469949, 'pulseName': 'test', 'columnId': 'status_1', 'columnType': 'color', 'columnTitle': 'Status', 'value': {'label': {'index': 0, 'text': 'Working on it', 'style': {'color': '#fdab3d', 'border': '#e99729', 'var_name': 'orange'}, 'is_done': False}, 'post_id': None}, 'previousValue': None, 'changedAt': 1733859434.833814, 'isTopGroup': False, 'triggerUuid': '82b14043bbd9b1dcb686a747fcdabf0f'}}
            # to a discord embed format
            elif data["event"]["type"] == "update_column_value":
                webhook_data = {
                    "embeds": [
                        {
                            "title": f"Task updated in {data['event']['groupName']}",
                            "url": f"https://flowdata.monday.com/boards/{data['event']['boardId']}/pulses/{data['event']['pulseId']}",
                            "description": f"Task **{data['event']['pulseName']}** changed to **{data['event']['value']['label']['text']}**",
                            "color": int(
                                data["event"]["value"]["label"]["style"][
                                    "color"
                                ].lstrip("#"),
                                16,
                            ),
                        }
                    ],
                }
            # Translate {'event': {'app': 'monday', 'type': 'create_update', 'triggerTime': '2024-12-10T19:40:04.266Z', 'subscriptionId': 444305404, 'userId': 55409066, 'originalTriggerUuid': None, 'boardId': 5992933181, 'pulseId': 8023469949, 'body': '<p>\ufeffsdfg</p>', 'textBody': 'sdfg', 'updateId': 3690127813, 'replyId': None, 'triggerUuid': 'ba09dcd6c8b1b6ec45df0ae891cb1707'}}
            # to a discord embed format
            elif data["event"]["type"] == "create_update":
                webhook_data = {
                    "embeds": [
                        {
                            "title": f"New update in monday",
                            "url": f"https://flowdata.monday.com/boards/{data['event']['boardId']}/pulses/{data['event']['pulseId']}",
                            "description": f"**{data['event']['pulseName']}** - {data['event']['textBody']}",
                        }
                    ],
                }
            else:
                # Ignore other event types
                return JSONResponse({"status": "ignored"}, 200)
            forward_response = requests.post(TARGET_URL, json=webhook_data)
            forward_response.raise_for_status()

            # Return a simple acknowledgment or the forwarded response if desired
            return JSONResponse(
                {
                    "status": "forwarded",
                    "forwarded_response_code": forward_response.status_code,
                    "forwarded_response_text": forward_response.text,
                },
                200,
            )
        except requests.RequestException as e:
            # Handle errors if the forward request fails
            return JSONResponse({"error": str(e)}, 500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
