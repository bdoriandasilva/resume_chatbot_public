from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import PromptTemplate
from backend.retriever import Retriever
from datetime import datetime



class ChatBot():
    """Chatbot Class
    This class encapsulates the functionality of the Resume Chatbot, which interacts with users to provide 
    information about the resume. It leverages OpenAI's language model, LangChain's retrieval tools, 
    and a custom prompt template to generate context-aware responses.
    """

    def __init__(self,
                 parameters: dict[str, any]):
        self.parameters = parameters
        self.chat = ChatOpenAI(verbose=True, temperature=0)
        self.retrieval_qa_chat_prompt = self.create_prompt()
        self.retriever = Retriever(self.parameters)
        self.vector_store = self.retriever.get_vector_store()
        self.chatbot_welcome_message = f"Hi there! I'm here to help you explore {parameters['resume_owner_name']}'s resume. Whether you're looking for his experience, skills, or qualifications, feel free to ask! This chatbot was developed entirely by {parameters['resume_owner_name']} himself to assist recruiters like you in quickly understanding his professional profile. How can I help you today?"

    def answer(self, query, conversation, conv_last_n_messages = 6, fake_conversation = False):
        """Generates a response to the user's query based on the resume data and conversation history.
        
        Args:
            query (str): The user's question or input.
            conversation (list): The history of the conversation between the user and the chatbot.
            conv_last_n_messages (int, optional): The number of recent messages to consider from the 
                conversation history. Defaults to 6.
            fake_conversation (bool, optional): If True, returns a fake response for testing purposes. 
                Defaults to False.
        
        Returns:
            dict: A dictionary containing the user's input, context, and the chatbot's response.
        """
        if fake_conversation:
            # Return fake answer to test the solution without using the paid services 
            result = {'input': 'Fake question', 'context': [], 'answer': 'This is a fake answer to test the solution without spending LLM tokens...'}
            return result
        else:
            chat = ChatOpenAI(verbose=True, temperature=0, model=self.parameters['llm_model'])

            # Process the conversation history to provide context for the chatbot.
            if len(conversation) > 2:
                # removing first and last message
                conversation = conversation[1:-1]
                # Keeping the last  "conv_last_n_messages" messages of the historic conversation
                if conv_last_n_messages is not None: 
                    conv_last_n_messages = conv_last_n_messages * -1
                    conv_hist = "\n".join([str(entry) for entry in conversation[conv_last_n_messages:]])  
                else:
                    # the entire historic conversation
                    conv_hist = "\n".join([str(entry) for entry in conversation])   
            else:
                conv_hist = 'There is no previous messages'        
            current_date = datetime.now()
            current_date = current_date.strftime("%B %d, %Y")

            stuff_documents_chain = create_stuff_documents_chain(chat, self.retrieval_qa_chat_prompt)
            qa = create_retrieval_chain(
                retriever=self.vector_store.as_retriever(search_type="hybrid"), combine_docs_chain=stuff_documents_chain)
            result = qa.invoke(input={"input": query, "history":conv_hist, "date": current_date, "resume_owner_name": self.parameters['resume_owner_name'] })
            return result
        
    def create_prompt(self):
        """Creates a custom prompt template for the chatbot.
        
        The prompt template instructs the chatbot to answer questions based on the provided context 
        (resume data), conversation history, and user input. It ensures that the chatbot focuses on 
        candidate qualifications, skills, and experiences.
        
        Returns:
            PromptTemplate: A LangChain prompt template for generating responses.
        """
        return PromptTemplate.from_template("""
        You are a helpful assistant specialized in answering questions related to the resume of {resume_owner_name}.
        Answer any use questions based solely on the context and conversation history shown below.
                                                  
        ### Context:
        Here is the relevant information retrieved from {resume_owner_name}'s resume:
        {context}
        Current system Date: {date}

        ### Conversation History:
        These are the previous exchanges between the user and the chatbot:
        {history}

        ### User Input:
        The user has just asked the following question:
        {input}

        ### Instructions:
        Based on the provided context, the conversation history, and the user's latest question, generate a helpful and accurate response that refers to **{resume_owner_name}** qualifications, skills, experiences, and other resume-related details. Ensure the response is clear and addresses the specific user query.
        """)

    def get_chatbot_welcome_message(self):
        """Returns the chatbot's welcome message.
        
        Returns:
            str: A welcome message introducing the chatbot and its purpose.
        """
        return self.chatbot_welcome_message
    