"""
summarizer.py
-------------
Sends the meeting transcript to the Groq API and asks the model to
produce four structured outputs: Summary, Minutes of Meeting (MoM),
Action Items, and Key Decisions.
"""

import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

# Instantiate the Groq client once. It reads the API key we pass explicitly
# (kept in config.py, sourced from an environment variable).
_client = Groq(api_key=GROQ_API_KEY)


# The system prompt tells the model exactly what role to play and, crucially,
# what output format to return so we can reliably parse it in Python.
_SYSTEM_PROMPT = """You are an expert meeting assistant.
You will be given a raw meeting transcript. Analyze it and produce a
structured breakdown.

Respond ONLY with a valid JSON object (no markdown fences, no extra text)
with exactly these keys:
{
  "summary": "A concise paragraph summarizing the overall meeting",
  "mom": "A well-structured Minutes of Meeting text with sections/topics discussed",
  "action_items": ["list", "of", "action item strings, each with an owner if mentioned"],
  "key_decisions": ["list", "of", "key decisions made during the meeting"]
}

If the transcript does not mention explicit owners for action items, just
describe the task. If there are no action items or decisions, return an
empty list for that field. Do not invent information that isn't in the
transcript.
"""


def generate_meeting_insights(transcript: str) -> dict:
    """
    Call the Groq API with the transcript and return a dictionary with
    keys: summary, mom, action_items, key_decisions.

    Raises:
        ValueError: if the transcript is empty.
        RuntimeError: if the API response can't be parsed as JSON.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty; nothing to summarize.")

    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.3,        # lower temperature = more consistent, factual output
        response_format={"type": "json_object"},  # ask Groq to enforce valid JSON
    )

    raw_content = response.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse model response as JSON: {e}\nRaw response: {raw_content}"
        )

    # Fill in any missing keys defensively so the rest of the app never
    # has to worry about KeyError.
    data.setdefault("summary", "")
    data.setdefault("mom", "")
    data.setdefault("action_items", [])
    data.setdefault("key_decisions", [])

    return data
