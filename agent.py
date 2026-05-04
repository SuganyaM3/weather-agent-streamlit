
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

APP_NAME = "weather_app"
USER_ID = "user_001"


def get_weather(city: str) -> dict:
    data = {
        "chennai": "Hot and humid, 35°C",
        "mumbai": "Humid, 31°C",
        "delhi": "Hazy, 32°C",
    }

    city = city.lower().strip()

    if city in data:
        return {"status": "success", "report": data[city]}

    return {"status": "error", "error_message": "City not supported"}


root_agent = Agent(
    name="weather",
    model="gemini-2.0-flash",   # 🔥 IMPORTANT CHANGE (more stable)
    instruction="Get city and respond shortly",
    tools=[get_weather],
)


async def run_agent_async(msg: str):
    session_service = InMemorySessionService()

    session_id = "temp_session"  # ✅ FIXED stable ID

    # ✅ MUST create session
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    from google.genai import types as genai_types

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=msg)],
    )

    reply = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            for part in event.content.parts:
                if hasattr(part, "text"):
                    reply += part.text

    return reply


def ask_agent(msg: str):
    try:
        return asyncio.run(run_agent_async(msg))
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_agent_async(msg))        