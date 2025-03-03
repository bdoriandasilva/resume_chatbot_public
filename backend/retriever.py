import os

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import OpenAIEmbeddings


class Retriever():
    """ Retriever Class
    This class encapsulates the functionality for retrieving and managing documents within the Azure AI Search index.
    It handles the creation of embeddings, interaction with the Azure AI Search service, and the loading of documents.
    It uses OpenAI's embeddings model to generate vector representations of the documents, which are then stored in the Azure AI Search index for efficient retrieval.
    """
    def __init__(self, parameters: dict[str, any]):
        self.parameters = parameters
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            openai_api_key=parameters['openai_api_key'], 
            openai_api_version=parameters['openai_api_version'], 
            model=parameters['model']
        )
        self.index_name: str = parameters['index_name']
        self.vector_store: AzureSearch = AzureSearch(
            azure_search_endpoint=parameters['azure_ai_search_url'],
            azure_search_key=parameters['azure_ai_search_api_key'],
            index_name=self.index_name,
            embedding_function=embeddings.embed_query,
        )
    
    def docx_loader(self, docx_file_path: str):
        """Loads documents from a DOCX file.

        Args:
            docx_file_path (str): The path to the DOCX file.

        Returns:
            list: A list of Document objects loaded from the DOCX file.
        """
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(docx_file_path)
        return loader.load()
    
    def upload_docs_index(self, docs):
        """Uploads documents to the Azure AI Search index.

        Args:
            docs (list): A list of Document objects to be uploaded.
        """

        self.vector_store.add_documents(documents=docs)

    def get_vector_store(self):
        """Retrieves the vector store object.

        Returns:
            AzureSearch: The vector store object.
        """
        return self.vector_store
    
