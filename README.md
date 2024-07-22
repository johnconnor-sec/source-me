# Local RAG AI Assistant

## Table of Contents
[Introduction](#introduction)|[Features](#features)|[Prerequisites](README.md#prerequisites)|[Installation](#installation)|[Usage](#usage)|[CLI Version](#cli-version)|[GUI Version](#gui-version)|[Project Structure](#project-structure)|[Configuration](#configuration)|[Development](#development)|[Contributing](#contributing)|[License](#license)|[Contact](#contact)

## Introduction

The Local RAG AI Assistant is a powerful tool that combines document management with AI-powered interactions. It allows users to process various document types, perform intelligent searches across their document collection, and engage in meaningful dialogues based on the processed information. All data is stored locally, ensuring privacy and security.

This project is built using Python, leveraging technologies such as Streamlit, LangChain, and Ollama for embeddings and chat completions. It uses a local PostgreSQL database for data storage.

## Features

- **Document Processing**: Upload and process TXT, MD, PDF, and CSV files.
- **Intelligent Search**: Find relevant information across your document collection.
- **AI-Powered Conversations**: Engage in context-aware dialogues based on your documents.
- **Local Database**: All data stays secure on your local machine.
- **Dual Interface**: Choose between a CLI and a GUI (Streamlit) version.
- **Data Analysis**: Analyze CSV files using PandasAI integration.
- **Customizable**: Built with modularity in mind for easy modifications and extensions.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Ollama (for embeddings and chat completions)
- PostgreSQL with pgvector extension

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/local-rag-ai-assistant.git
   cd source.me
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
│   ├── assistant.py
│   ├── README.md
│   └── requirements.txt
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
