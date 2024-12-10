import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
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
        return Response(data, 200)
    else:
        # Forward the request data to the target URL
        try:
            forward_response = requests.post(TARGET_URL, json=data)
            forward_response.raise_for_status()

            # Return a simple acknowledgment or the forwarded response if desired
            return Response(
                {
                    "status": "forwarded",
                    "forwarded_response_code": forward_response.status_code,
                    "forwarded_response_text": forward_response.text,
                },
                200,
            )
        except requests.RequestException as e:
            # Handle errors if the forward request fails
            return Response({"error": str(e)}, 500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
