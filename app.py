from dotenv import load_dotenv
import os
load_dotenv()
from config.configuration import load_config
from backend.chatbot import ChatBot
from backend.db_manager import DBManager
from typing import Set
import streamlit as st
import streamlit_authenticator as stauth 

import yaml
from yaml.loader import SafeLoader

config_path = os.path.join('streamlit', 'config.conf')

with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

parameters = load_config()

# Load the users information
db_manager = DBManager(parameters)
config['credentials']['usernames'] = db_manager.get_users_info() 

chatbot = ChatBot(parameters)

# App title
st.set_page_config(page_title="Resume Chatbot")

# --- USER AUTHENTICATION ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    # validate the max limit of user messages
    user_id = db_manager.get_user_id(st.session_state["username"])
    if not db_manager.validate_user_max_messages(user_id):
        error_message = f"Oops! Message limit reached. To continue chatting, please contact {parameters['resume_owner_name']} to request an increase in your message limit. He can adjust your account for extended access."
        st.error(error_message, icon="🚨")
    else:        
        # Store LLM generated responses
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "assistant", "content": chatbot.get_chatbot_welcome_message()}]

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Function for generating LLM response
        def generate_response(prompt_input ,conversation):
            "Function for generating LLM response"
            generated_response = chatbot.answer(query=prompt_input, conversation=conversation, fake_conversation=False)
            formatted_response = (
                    f"{generated_response['answer']}"
                )
            return formatted_response

        # User-provided prompt
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        # Generate a new response if last message is not from assistant
        if st.session_state.messages[-1]["role"] != "assistant":        
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):                
                    response = generate_response(prompt, st.session_state.messages) 
                    st.write(response) 
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)        
            db_manager.insert_conversation(user_id, prompt, response )
        
    
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')   
 