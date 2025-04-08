import streamlit as st
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()  

API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)


# Load JSON data with increased size limit
def load_json(file_path, max_size=800000):  # Increased size limit to 8 lacs
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Convert JSON to string
        json_text = json.dumps(data, indent=2)

        # Truncate JSON if too large
        if len(json_text) > max_size:
            json_text = json_text[:max_size] + "... (truncated)"
        
        return json_text, data  # Return both raw text and parsed JSON
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return None, None

# Define structured query mapping
DATA_MAPPINGS = {
    "exdata_fabric": ["Article Name", "Fabric", "Fancy Name", "Name", "Item", "Article", "Fabric Name"],
    "exdata_weave": ["Weave"],
    "exdata_content": ["Composition", "Content", "Mixture"],
    "exdata_color": [],
    "exdata_ref": [],
    "exdata_weight": ["Weight", "Oz"],
    "exdata_widthin": ["Width in Inches", "Width(in)", "width"],
    "exdata_widthcm": ["Width in Centimeters", "Width in cm", "Width(cm)", "Width"],
    "exdata_stretch": ["Stretch"],
    "exdata_growth": ["Growth"],
    "exdata_finish": ["PRE-SKEWED & SEMI SHRUNK", "Finishing Route", "Finish Name", "Finish"],
    "exdata_weightaw": ["Weight After Wash", "After Wash Weight", "Weight"],
    "exdata_wash": ["Wash Code", "Wash Recipe", "Recipe Name"],
    "elongation": ["Elongation"],
    "dye": ["Dye Name", "Dye", "Chemical"],
    "yarn_size_warp": ["Warp"],
    "yarn_size_weft": ["Weft"]
}

# Query LLM with structured data understanding
import json

def query_llm(prompt, json_data):
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    # Build structured prompt with necessary context
    structured_prompt = (
        "You are an AI assistant analyzing structured JSON data. "
        "Answer queries accurately based on the given JSON structure. "
        "Answer all type of queries"
        "If a query asks for a proper format, ensure to respond in the exact format provided in the data file. "
        "if user ask for all data based on query show all data of it, show the data has this fields not like all info of it , if asked to show then show "
        "If the data is in an inconsistent format, convert it into a consistent format as outlined in the data file.\n\n"
        "User Query: " + prompt + "\n\n"
        "Relevant Data:\n" + json.dumps(json_data, indent=2)[:800000]  # Limit JSON size sent to API
    )

    try:
        response = model.generate_content([structured_prompt])
        return response.text.strip() if response else "No response received."
    except Exception as e:
        st.error(f"Error querying LLM: {e}")
        return None


# Streamlit UI
st.title("Chat with AI AGENT")

file_path = r"D:\\code of llm\\data.json"  # Replace with your actual JSON file path
json_text, json_data = load_json(file_path)

if json_text:
    st.success("JSON loaded successfully! Ask any query.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Ask a question about the data...")
    if prompt:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from LLM
        response = query_llm(prompt, json_data)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
