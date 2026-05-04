
import asyncio
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

APP_NAME = "weather_app"
USER_ID = "user_001"


# ── TOOL ──────────────────────────────────────────────────────────────────────
def get_weather(city: str) -> dict:
    weather_data = {
        "san francisco": {"status": "success", "report": "Sunny, 22°C, low humidity."},
        "new york":      {"status": "success", "report": "Cloudy, 18°C, chance of rain."},
        "london":        {"status": "success", "report": "Rainy, 14°C, carry an umbrella!"},
        "tokyo":         {"status": "success", "report": "Clear, 21°C, perfect weather."},
        "paris":         {"status": "success", "report": "Partly cloudy, 20°C."},
        "chennai":       {"status": "success", "report": "Hot & humid, 35°C."},
        "mumbai":        {"status": "success", "report": "Humid, 31°C, monsoon vibes."},
        "delhi":         {"status": "success", "report": "Hazy, 32°C, moderate AQI."},
        "sydney":        {"status": "success", "report": "Sunny, 25°C."},
        "dubai":         {"status": "success", "report": "Very hot, 40°C."},
        "bangalore":     {"status": "success", "report": "Pleasant, 26°C."},
        "hyderabad":     {"status": "success", "report": "Warm, 30°C."},
    }

    city_lower = city.lower().strip()

    if city_lower in weather_data:
        return weather_data[city_lower]

    return {
        "status": "error",
        "error_message": "City not supported. Try Chennai, Mumbai, Delhi, etc."
    }


# ── AGENT ─────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash",
    instruction="""
    You are Sunny, a friendly weather assistant.
    Extract city → call get_weather → reply in 1–2 lines.
    """,
    tools=[get_weather],
)


# ── CORE EXECUTION ────────────────────────────────────────────────────────────
async def run_agent_async(user_message: str) -> str:
    session_id = str(uuid.uuid4())  # always fresh

    session_service = InMemorySessionService()

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

    # ⚡ IMPORTANT: let runner auto-create session (do NOT pre-create)
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    reply += part.text

    return reply or "⚠️ Unable to fetch weather. Try again."


# ── SYNC WRAPPER ──────────────────────────────────────────────────────────────
def ask_agent(user_message: str) -> str:
    try:
        return asyncio.run(run_agent_async(user_message))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_agent_async(user_message))
        