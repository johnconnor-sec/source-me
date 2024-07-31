# Local RAG AI Assistant

## Table of Contents
[Introduction](README.md#introduction)|[Features](README.md#features)|[Prerequisites](README.md#prerequisites)|[Installation](README.md#installation)|[Usage](README.md#usage)|[CLI Version](README.md#cli-version)|[GUI Version](README.md#gui-version)|[Project Structure](README.md#project-structure)|[Configuration](README.md#configuration)|[Development](README.md#development)|[Contributing](README.md#contributing)|[License](README.md#license)|[Contact](README.md#contact)

## Introduction

The Local RAG AI Assistant is a powerful tool that combines document management with AI-powered interactions. It allows users to process various document types, perform intelligent searches across their document collection, and engage in meaningful dialogues based on the processed information. All data is stored locally, ensuring privacy and security.

This project is built using Python, leveraging technologies such as Streamlit, LangChain, and Ollama for embeddings and chat completions. It uses a local PostgreSQL database for data storage.

## Program Objectives

The Local RAG AI Assistant aims to:

1. **Enhance Document Management**: Provide an efficient way to process, store, and retrieve information from various document types.

2. **Facilitate Knowledge Discovery**: Enable users to uncover insights and connections across their document collection that might not be immediately apparent.

3. **Offer Intelligent Assistance**: Leverage AI to provide context-aware responses and assist with complex queries related to the user's documents.

4. **Ensure Data Privacy**: Keep all data and processing local, giving users full control over their information.

5. **Streamline Workflow**: Integrate document analysis, search, and AI-powered interactions into a single, user-friendly interface.

6. **Support Data-Driven Decision Making**: Help users make informed decisions by providing quick access to relevant information from their document collection.

7. **Promote Customization and Extensibility**: Offer a flexible framework that can be adapted to various use cases and extended with new features.

## Features

- **Document Processing**: Upload and process TXT, MD, PDF, and CSV files.
- **Intelligent Search**: Find relevant information across your document collection.
- **AI-Powered Conversations**: Engage in context-aware dialogues based on your documents.
- **Local Database**: All data stays secure on your local machine.
- **Dual Interface**: Choose between a CLI and a GUI (Streamlit) version.
- **Data Analysis**: Analyze CSV files using PandasAI integration.
- **Customizable**: Built with modularity in mind for easy modifications and extensions.

## Best Practices for Usage

To get the most out of the Local RAG AI Assistant, consider the following best practices:

1. **Organize Your Documents**: Before uploading, organize your documents into logical categories. This can help with more efficient retrieval and analysis.

2. **Use Descriptive File Names**: When uploading documents, use clear and descriptive file names. This can aid in document management and search.

3. **Chunk Large Documents**: If you have very large documents, consider breaking them into smaller, topic-focused files. This can improve processing speed and retrieval accuracy.

4. **Utilize the Search Function**: Before asking questions, try using the search function to find relevant documents. This can provide context for more specific questions.

5. **Ask Specific Questions**: When interacting with the AI, ask clear and specific questions. This helps the system provide more accurate and relevant responses.

6. **Iterate on Queries**: If you don't get the desired information in the first response, try rephrasing your question or breaking it down into smaller parts.

7. **Regularly Update Your Document Collection**: Keep your document collection up-to-date by adding new documents and removing outdated ones. This ensures the AI has the most current information to work with.

8. **Experiment with Different Document Types**: Try using a mix of document types (TXT, MD, PDF, CSV) to see how the system handles different formats and what works best for your needs.

9. **Use Data Analysis Features**: For CSV files, take advantage of the PandasAI integration to perform detailed data analysis and gain insights from your structured data.

10. **Provide Feedback**: If you encounter any issues or have suggestions for improvement, use the provided channels to give feedback. This helps in continually improving the system.

11. **Monitor System Performance**: Keep an eye on processing times and system resource usage, especially when working with large document collections. This can help you optimize your usage.

12. **Ensure Regular Backups**: While all data is stored locally, it's good practice to regularly backup your document collection and database.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Ollama (for embeddings and chat completions) (https://ollama.com)
- PostgreSQL with pgvector extension

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/local-rag-ai-assistant.git
   cd local-rag-ai-assistant
   ```

2. Set up the environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   docker-compose up -d pgvector
   ```

5. Initialize the database:
   ```
   docker exec -it pgvector-container psql -U langchain -d langchain -c 'CREATE EXTENSION vector;'
   ```

## Usage

### CLI Version

To use the CLI version of the assistant:

1. Navigate to the `cli` directory:
   ```
   cd cli
   ```

2. Run the assistant:
   ```
   python assistant.py
   ```

3. Follow the on-screen prompts to interact with the assistant.

### GUI Version

To use the GUI (Streamlit) version of the assistant:

1. Navigate to the `gui` directory:
   ```
   cd gui
   ```

2. Start the Streamlit app:
   ```
   streamlit run main.py
   ```

3. Open your web browser and go to `http://localhost:8501` to interact with the assistant.

## Project Structure

```
.
├── cli
|   | main.py
|   | config.py
|   | database/
│   ├── __init__.py
│   ├── connection.py
│   └── operations.py
├── embedding/
│   ├── __init__.py
│   └── embed.py
├── document_processing/
│   ├── __init__.py
│   ├── loader.py
│   └── splitter.py
├── retrieval/
│   ├── __init__.py
│   └── similarity.py
├── chat/
│   ├── __init__.py
│   └── ollama_chat.py
└── utils/
    ├── __init__.py
    └── output.py
├── gui
│   ├── config.toml
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   ├── init-db.sh
│   ├── main.py
│   ├── media
│   │   └── JC-Profile-Update.png
│   ├── pages
│   │   ├── analysist.py
│   │   └── app.py
│   ├── requirements.txt
│   └── utils
│       ├── assistant.py
│       └── __init__.py
```

## Configuration

- Database configuration can be modified in `gui/utils/assistant.py` and `cli/assistant.py`.
- Streamlit configuration can be adjusted in `gui/config.toml`.
- Docker settings can be changed in `gui/docker-compose.yaml` and `gui/Dockerfile`.

## Development

To contribute to the project or customize it for your needs:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test thoroughly.
4. Submit a pull request with a clear description of your changes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please open an issue on the GitHub repository or contact the project maintainer at your@email.com.

---

Thank you for using the Local RAG AI Assistant! We hope it enhances your document management and AI interaction experience.
