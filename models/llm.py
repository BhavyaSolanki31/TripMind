import time
from google import genai
from dotenv import load_dotenv
import os


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



MODEL_NAME = "gemini-3.5-flash"



def ask_ai(prompt):

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            return response.text


        except Exception as e:

            print(
                f"AI attempt {attempt+1} failed..."
            )

            if attempt == 2:

                return (
                    "AI recommendation unavailable. "
                    "Using rule-based recommendation."
                )


            time.sleep(5)






def ask_ai_json(prompt):

    import json
    import time


    for attempt in range(3):

        try:

            response = client.models.generate_content(

                model="gemini-3.5-flash",

                contents=prompt

            )


            text = response.text.strip()


            if not text:
                raise Exception(
                    "Empty Gemini response"
                )


            # Remove markdown JSON wrapper

            if text.startswith("```"):

                text = (
                    text
                    .replace("```json","")
                    .replace("```","")
                    .strip()
                )


            json.loads(text)


            return text



        except Exception as e:

             error=str(e)


             if "429" in error or "RESOURCE_EXHAUSTED" in error:

                 print(
            "⚠️ Gemini quota exhausted. Using fallback."
        )

        return None


    print(
        f"AI attempt {attempt+1} failed..."
    )

    time.sleep(5)