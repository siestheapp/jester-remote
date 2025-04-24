import openai
import base64
import os
from dotenv import load_dotenv
from ..utils.vector_mapper import match_to_standard

# Load the .env file
env_loaded = load_dotenv("config.env")
print(f"✅ .env loaded? {'Yes' if env_loaded else 'No'}")

# Retrieve the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API KEY FOUND? {'Yes' if api_key else 'No'}")

# Set it for the OpenAI SDK
openai.api_key = api_key


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_vision_prompt(image_path):
    base64_image = image_to_base64(image_path)

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Here is a screenshot of a clothing size chart. "
                            "Extract the measurements in structured JSON format. "
                            "Do NOT double chest or waist values unless the label explicitly says something like '1/2 chest', 'pit to pit', or 'body width'. "
                            "If it only says 'Chest' or 'Waist', assume it's a full-body circumference. "
                            "Make sure the size chart is returned with clear measurement labels for each size."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    path = "uploads/sample_size_guide.jpg"
    vision_output = run_vision_prompt(path)
    print("🧠 GPT-4 Vision Output:")
    print(vision_output)

    print("\n🧬 Vector Match Example:")
    print(match_to_standard("Pit to Pit"))  # Expected: ('chest', ~0.90+ similarity)
