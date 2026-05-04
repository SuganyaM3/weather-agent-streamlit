
import asyncio
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

APP_NAME = "weather_app"
USER_ID = "user_001"


# ── TOOL ──────────────────────────────────────────────────────────────
def get_weather(city: str) -> dict:
    weather_data = {
        "chennai": "Hot and humid, 35°C",
        "mumbai": "Humid, 31°C",
        "delhi": "Hazy, 32°C",
        "bangalore": "Pleasant, 26°C",
        "hyderabad": "Warm, 30°C",
    }

    city = city.lower().strip()

    if city in weather_data:
        return {"status": "success", "report": weather_data[city]}

    return {"status": "error", "error_message": "City not supported"}


# ── AGENT ─────────────────────────────────────────────────────────────
root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash",
    instruction="Get city → call tool → reply short",
    tools=[get_weather],
)


# ── CORE FIX ──────────────────────────────────────────────────────────
async def run_agent_async(user_message: str) -> str:
    session_id = str(uuid.uuid4())

    session_service = InMemorySessionService()

    # ✅ CRITICAL FIX — create session BEFORE runner
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
        parts=[genai_types.Part(text=user_message)],
    )

    reply = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    reply += part.text

    return reply or "No response"


# ── SYNC WRAPPER ──────────────────────────────────────────────────────
def ask_agent(user_message: str) -> str:
    try:
        return asyncio.run(run_agent_async(user_message))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_agent_async(user_message))
        