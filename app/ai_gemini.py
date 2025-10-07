import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
def generate_trip_plan(destination, days, budget, companions):
    prompt = f"""
    Plan a {days}-day trip to {destination}.
    Budget: {budget}
    Traveling with: {companions}

    Include:
    - Top 3 attractions per day
    - Best visiting times
    - Famous local food suggestions
    - Estimated total trip cost in INR
    - A motivational travel quote to end.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# if __name__ == "__main__":
#     plan = generate_trip_plan("Goa", 3, "Moderate", "Friends")
#     print(plan)
