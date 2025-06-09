from app.utils import clone_repo
import os
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq


load_dotenv()
groq_api_key= os.getenv("GROQ_API_KEY")

# Initialize Groq LLM for LangChain
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama3-70b-8192",
    temperature=0.3
)

# Create the prompt
prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        "You are a senior developer. Given the following repo context:\n\n{context}\n\n"
        "Write a complete README.md with these sections: Title, Description, Installation, Usage, Contributing, License."
    )
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt)


def generate_readme_from_repo(repo_url: str) -> str:
    repo_path = clone_repo(repo_url)

    file_data = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.txt', '.json')):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                        file_data.append(f"## {relative_path}\n{content}")
                except Exception as e:
                    print(f"Skipping file {file}: {e}")

    # Combine all file content
    full_text = "\n\n".join(file_data)

    # STEP 1: Split content into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = text_splitter.create_documents([full_text])

    # STEP 2: Create embeddings using Hugging Face model
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # STEP 3: Store chunks in Chroma (in-memory)
    vectorstore = Chroma.from_documents(documents, embedding_model)

    # STEP 4: Retrieve top relevant chunks using a semantic query
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.get_relevant_documents("Generate a professional README.md for this GitHub project.")

    # STEP 5: Join retrieved content
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # STEP 6: Generate the README using the LLM chain
    try:
        readme = chain.run(context=context)
        return readme
    except Exception as e:
        return f"Error generating README: {e}"
