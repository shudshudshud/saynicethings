import streamlit as st
import google.generativeai as genai
from typing import Optional

# Set page configuration
st.set_page_config(
    page_title="Say Nice Things",
    page_icon="💐",
    layout="centered"
)

# Function to generate nice things using Gemini
def generate_nice_things(prompt: str, previous_response: Optional[str] = None) -> str:
    """Generate nice things to say about someone based on prompt."""
    try:
        # This is where you'll connect to Gemini API
        if st.session_state.get('use_api'):
            model = genai.GenerativeModel('gemini-flash-2.0')
            
            if previous_response:
                # Include previous response for refinement
                full_prompt = f"""
                Previous nice message: {previous_response}
                
                User wants to refine this with additional context: {prompt}
                
                Generate a refined, heartfelt message that incorporates both the previous message and this new context.
                The message should be personal, specific, authentic, and warm.
                """
            else:
                # First-time generation
                full_prompt = f"""
                Help me say something nice about a person based on this stream of consciousness: {prompt}
                
                Create a heartfelt message that I could share with them that sounds natural and specific.
                Focus on their positive qualities, actions, or impact.
                Make it personal, authentic, and warm rather than generic.
                Keep it concise (2-4 sentences).
                """
            
            response = model.generate_content(full_prompt)
            return response.text
        else:
            # Placeholder response when API is not connected
            if previous_response:
                return f"This would refine the previous message using the Gemini API, incorporating: '{prompt}'"
            else:
                return f"This would use the Gemini API to transform your thoughts into a nice message about: '{prompt}'"
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Initialize session state for conversation history
if 'history' not in st.session_state:
    st.session_state.history = []
    
if 'current_nice_thing' not in st.session_state:
    st.session_state.current_nice_thing = None
    
# Initialize API connection
if 'use_api' not in st.session_state:
    st.session_state.use_api = False
    # Try to load API key from Streamlit secrets
    try:
        if "google" in st.secrets and "api_key" in st.secrets["google"]:
            api_key = st.secrets["google"]["api_key"]
            genai.configure(api_key=api_key)
            st.session_state.use_api = True
    except Exception:
        # If secrets aren't available, we'll use the manual input option
        pass

# App header
st.title("💐 Say Nice Things")
st.markdown("""
Transform your thoughts into heartfelt compliments and messages of appreciation.
Simply share your stream of consciousness about someone, and we'll help you craft something nice to say.
""")

# API connection status and manual connection option
with st.sidebar:
    st.header("API Settings")
    
    api_status = "✅ Connected" if st.session_state.use_api else "❌ Not connected"
    st.info(f"Gemini API Status: {api_status}")
    
    # Only show manual connection if not already connected
    if not st.session_state.use_api:
        st.markdown("##### Connect API")
        api_key = st.text_input("Google API Key", type="password", 
                              help="Enter your Google API key to enable Gemini Flash 2.0")
        connect_button = st.button("Connect API")
        
        if connect_button and api_key:
            try:
                # Configure API
                genai.configure(api_key=api_key)
                st.session_state.use_api = True
                st.success("✅ API connected successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to connect: {str(e)}")
    
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
    1. Enter your thoughts about someone
    2. Click "Generate Nice Thing to Say"
    3. Refine as needed with additional context
    4. Copy your final message
    """)

# Main input area
user_input = st.text_area(
    "Your thoughts about the person",
    height=150,
    placeholder="I was thinking about my coworker Alex today and how they helped me with that project last week. They stayed late to make sure it was done right and never complained. They're always so patient explaining things..."
)

# Button to generate or refine
button_text = "Refine This Message" if st.session_state.current_nice_thing else "Generate Nice Thing to Say"
if st.button(button_text, type="primary"):
    if user_input:
        # Generate or refine response
        response = generate_nice_things(user_input, st.session_state.current_nice_thing)
        
        # Save to history and current state
        st.session_state.history.append((user_input, response))
        st.session_state.current_nice_thing = response
        
        # Clear input for refinement
        # We'll keep the input for this demo to make refinement easier
        # st.experimental_rerun()

# Display current response
if st.session_state.current_nice_thing:
    st.markdown("### Your Nice Message")
    message_container = st.container(border=True)
    
    with message_container:
        st.markdown(st.session_state.current_nice_thing)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Copy to Clipboard"):
                st.toast("Message copied to clipboard!")

# History section (collapsible)
if st.session_state.history:
    with st.expander("View Message History", expanded=False):
        for i, (input_text, response) in enumerate(st.session_state.history):
            st.markdown(f"**Iteration {i+1}**")
            st.markdown(f"*Your thoughts:* {input_text}")
            st.markdown(f"*Nice message:* {response}")
            st.markdown("---")

# Reset button
if st.session_state.current_nice_thing:
    if st.button("Start New Message"):
        st.session_state.current_nice_thing = None
        # Don't clear history
        st.experimental_rerun()