def generate_itinerary_with_agent(place, start_date, end_date):

    import requests
    from langchain.tools import tool
    from langchain.agents import initialize_agent, AgentType
    from langchain_google_genai import ChatGoogleGenerativeAI

    def safe_get_json(resp):
        try:
            return resp.json()
        except Exception as e:
            print("Failed to parse JSON:", e)
            print("Status code:", resp.status_code)
            print("Response text:", resp.text[:500])
            return None

    def get_city_coords(city):
        url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
        headers = {
            "User-Agent": "project.ipynb/1.0 (goyalshubham.2811@gmail.com)"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            geo = safe_get_json(resp)
            if not geo:
                print(f"No geocoding result for city: {city}")
                return None, None
            return geo[0]['lat'], geo[0]['lon']
        except Exception as e:
            print(f"Error in get_city_coords: {e}")
            return None, None

    def search_places(city):
        lat, lon = get_city_coords(city)
        if not lat or not lon:
            return []
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={lat}|{lon}&gslimit=5&format=json"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = safe_get_json(resp)
            return [place['title'] for place in data.get('query', {}).get('geosearch', [])] if data else []
        except Exception as e:
            print(f"Error in search_places: {e}")
            return []

    def getweather(city):
        lat, lon = get_city_coords(city)
        if not lat or not lon:
            return {}
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = safe_get_json(resp)
            return data.get('current_weather', {}) if data else {}
        except Exception as e:
            print(f"Error in getweather: {e}")
            return {}

    def findhotels(city):
        lat, lon = get_city_coords(city)
        if not lat or not lon:
            return []
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node
        ["tourism"="hotel"]
        (around:5000,{lat},{lon});
        out;
        """
        try:
            resp = requests.post(overpass_url, data={
                                 'data': query}, timeout=20)
            resp.raise_for_status()
            data = safe_get_json(resp)
            return [el['tags'].get('name', 'Unnamed Hotel') for el in data.get('elements', [])][:5] if data else []
        except Exception as e:
            print(f"Error in findhotels: {e}")
            return []

    def suggest_itinerary(city, days):
        places = search_places(city)
        if not places:
            return ["No places found."]
        itinerary = []
        for i in range(days):
            place = places[i % len(places)]
            itinerary.append(f"Day {i+1}: Visit {place}")
        return itinerary

    @tool
    def search_places_tool(city: str) -> list:
        """Return a list of the most notable tourist attractions and places to visit in the given city. Use this to get real, up-to-date places for itinerary planning."""
        return search_places(city)

    @tool
    def getweather_tool(city: str) -> dict:
        """Get the current weather for a given city using open APIs."""
        return getweather(city)

    # def findhotels_tool(city: str) -> list:
    #  """Return a list of recommended hotels in the given city. Use this to suggest hotels for each day of the itinerary."""
    #   return findhotels(city)

    @tool
    def suggest_itinerary_tool(input: str) -> list:
        """
        Suggest a travel itinerary for a given city and number of days.
        Input should be 'city, days' or 'city, days, [optional extra info]'.
        """
        parts = [p.strip() for p in input.split(",")]
        if len(parts) < 2:
            return ["Error: Please provide input as 'city, days'."]
        city = parts[0]
        try:
            days = int(parts[1])
        except ValueError:
            return ["Error: Number of days must be an integer."]
        # Optionally, use parts[2:] for extra info (e.g., "tourist")
        return suggest_itinerary(city, days)

    # from langchain_community.llms import HuggingFaceHub

    # llm = HuggingFaceHub(
        # repo_id="HuggingFaceH4/zephyr-7b-alpha",  # or your chosen model
        # model_kwargs={"temperature": 0.7, "max_new_tokens": 512}
    # )
    """
    from langchain_huggingface.llms.huggingface_endpoint import HuggingFaceEndpoint
    llm = HuggingFaceEndpoint(
        task="text-generation",  # Or "text2text-generation"
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        temperature=0.7,    # Adjust for creativity
        huggingfacehub_api_token="YOUR API KEY",
        provider="hf-inference"
    )
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", google_api_key="YOUR API KEY")

    tools = [search_places_tool, getweather_tool, suggest_itinerary_tool]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    response = agent.run(
        f"""Generate a detailed travel itinerary for a trip to {place} from {start_date} to {end_date}. Please include:
        Daily breakdown: A day-by-day plan with specific activities, attractions, and recommended timings.
        Weather considerations: Suggest activities and packing advice based on the typical weather conditions in {place} during {start_date} to {end_date}. Mention average temperatures and precipitation.
        Transportation: Recommendations for getting around within the destination.
        Accommodation suggestions: Briefly mention the type of accommodation (e.g., budget, mid-range, luxury) that would be suitable.
        Food recommendations: Highlight local dishes or restaurants to try.
        Optional activities: Include a few additional suggestions for free time or if certain plans change.
        Practical tips: Any essential travel tips for the destination (e.g., currency, language, safety).
        Please present the itinerary in a clear and organized format."""
    )
    return response
