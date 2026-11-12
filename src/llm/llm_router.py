
import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

# =====================================================
# CLIENT INITIALIZATION
# =====================================================

openrouter_client = None
groq_client = None

if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)


# =====================================================
# JSON EXTRACTION
# =====================================================

def extract_json(content):
    if not content:
        raise ValueError("LLM returned an empty response")

    content = content.strip()

    # First try parsing the complete response
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Handle JSON embedded in Markdown or extra text
    decoder = json.JSONDecoder()

    for index, char in enumerate(content):
        if char in "[{":
            try:
                parsed, _ = decoder.raw_decode(content[index:])
                return parsed
            except json.JSONDecodeError:
                continue

    raise ValueError("No valid JSON found in LLM response")


# =====================================================
# CORE LLM ROUTER
# =====================================================

def chat_completion(system_prompt, user_prompt, temperature=0.2):

    # -------------------------------------------------
    # 1. OPENROUTER - PRIMARY (META LLAMA)
    # -------------------------------------------------

    if openrouter_client is not None:
        try:
            response = openrouter_client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=temperature
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("OpenRouter returned empty content")

            print("LLM Model:", OPENROUTER_MODEL)

            return {
                "llm_used": "openrouter-llama",
                "content": content
            }

        except Exception as e:
            print("OpenRouter error:", str(e))

    # -------------------------------------------------
    # 2. GROQ - BACKUP
    # -------------------------------------------------

    if groq_client is not None:
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=temperature
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Groq returned empty content")

            print("LLM Provider: Groq")

            return {
                "llm_used": "groq",
                "content": content
            }

        except Exception as e:
            print("Groq error:", str(e))

    # -------------------------------------------------
    # 3. HARD FALLBACK
    # -------------------------------------------------

    return {
        "llm_used": "none",
        "content": json.dumps({
            "risk_level": "UNKNOWN",
            "explanation": "All LLM providers failed. Manual review required.",
            "regulation": "N/A"
        })
    }


# =====================================================
# JSON RESPONSE HANDLER
# =====================================================

def chat_completion_json(system_prompt, user_prompt, temperature=0.2):

    result = chat_completion(
        system_prompt,
        user_prompt,
        temperature
    )

    content = result["content"]
    provider = result["llm_used"]

    try:
        parsed = extract_json(content)

        # Expected format for clause extraction
        if isinstance(parsed, list):
            return {
                "data": parsed,
                "_llm_used": provider
            }

        # Preserve object responses
        if isinstance(parsed, dict):
            parsed["_llm_used"] = provider
            return parsed

        raise ValueError("LLM returned an unsupported JSON type")

    except Exception as e:
        print("JSON parsing error:", str(e))
        print("Raw LLM response:", content)

        return {
            "data": [],
            "_llm_used": provider,
            "_llm_error": str(e)
        }
