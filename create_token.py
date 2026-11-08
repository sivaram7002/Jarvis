import os
from datetime import timedelta
from dotenv import load_dotenv
from livekit import api

load_dotenv(".env.local")

api_key = os.getenv("LIVEKIT_API_KEY", "APIUKc3RmbZ7x7C")
api_secret = os.getenv("LIVEKIT_API_SECRET", "SHNep382bhAJMW4y1Kk6efg1nBWZ7MgjG3ia7h2EHlqB")

token = (
    api.AccessToken(api_key, api_secret)
    .with_identity("Shazam")
    .with_name("Shazam")
    .with_grants(
        api.VideoGrants(
            room_join=True,
            room="console-fe617493",
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )
    )
    .with_ttl(timedelta(days=365))
)

jwt_token = token.to_jwt()
print("\nGenerated Shazam Token with Full Audio & Data Grants:\n")
print(jwt_token)
print("\n")