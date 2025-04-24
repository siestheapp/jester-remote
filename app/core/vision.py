import openai
import base64
import os
import json
import datetime
from dotenv import load_dotenv
from ..utils.vector_mapper import match_to_standard

# Load the .env file
env_loaded = load_dotenv()
print(f"✅ .env loaded? {'Yes' if env_loaded else 'No'}")

# Retrieve the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API KEY FOUND? {'Yes' if api_key else 'No'}")

# Set it for the OpenAI SDK
openai.api_key = api_key


def image_to_base64(path):
    """Convert an image file to base64 encoding."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_vision_prompt(image_path):
    """Run GPT-4 Vision analysis on a size guide image."""
    base64_image = image_to_base64(image_path)

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
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


def process_size_guide_image(image_path: str, metadata: dict = None) -> dict:
    """
    Process a size guide image and return structured data.
    
    Args:
        image_path: Path to the size guide image
        metadata: Optional metadata about the size guide
        
    Returns:
        dict: Structured data containing the size guide information
    """
    # Get the raw vision analysis
    vision_output = run_vision_prompt(image_path)
    
    try:
        # Try to parse the JSON from the vision output
        # First, find the JSON part of the response
        json_start = vision_output.find('{')
        json_end = vision_output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = vision_output[json_start:json_end]
            size_data = json.loads(json_str)
            
            # Add metadata
            size_data['metadata'] = {
                'source_image': os.path.basename(image_path),
                'processed_timestamp': str(datetime.datetime.now()),
                'raw_vision_output': vision_output,
                **(metadata or {})  # Include provided metadata if available
            }
            
            return size_data
        else:
            raise ValueError("No JSON found in vision output")
            
    except (json.JSONDecodeError, ValueError) as e:
        # If JSON parsing fails, return a structured error response
        return {
            'error': str(e),
            'raw_vision_output': vision_output,
            'metadata': {
                'source_image': os.path.basename(image_path),
                'processed_timestamp': str(datetime.datetime.now()),
                **(metadata or {})  # Include provided metadata if available
            }
        }


if __name__ == "__main__":
    path = "uploads/sample_size_guide.jpg"
    vision_output = run_vision_prompt(path)
    print("🧠 GPT-4 Vision Output:")
    print(vision_output)

    print("\n🧬 Vector Match Example:")
    print(match_to_standard("Pit to Pit"))  # Expected: ('chest', ~0.90+ similarity)
