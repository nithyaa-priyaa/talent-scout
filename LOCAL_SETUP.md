Local Installation and Environment Setup

This guide provides step-by-step instructions to configure and run the Catalyst Talent Engine on a local machine.

1. Prerequisites
Python 3.10 or higher: Required for compatibility with Sentence-Transformers.
Homebrew (macOS): Recommended for managing Python versions and dependencies.
Groq API Key: Required for the Agentic Engagement module.

2. Repository Initialization
Clone the repository and navigate into the project directory:
Bash
git clone https://github.com/nithyaapriyaa/talent-scout.git
cd talent-scout

3. Virtual Environment Configuration
It is recommended to use a virtual environment to avoid dependency conflicts.
macOS/Linux:
If Python is not installed, use Homebrew: brew install python.
Then, create and activate the environment:
Bash
python3 -m venv venv
source venv/bin/activate
Windows:
Bash
python -m venv venv
venv\Scripts\activate

4. Dependency Installation
Install the required libraries using the provided requirements file:
Bash
pip install --upgrade pip
pip install -r requirements.txt

5. Environment Secrets
The application requires an API key to communicate with the Groq LLM. Create a file named .env in the root directory and add your key:
GROQ_API_KEY=your_gsk_key_here
Note: Do not commit the .env file to version control.

6. Executing the Application
Launch the Streamlit interface:
Bash
streamlit run app.py
The application will be accessible at http://localhost:8501.

7. Troubleshooting and Common Fixes
ModuleNotFoundError (torch or torchvision):
The Transformers library may require explicit installation of the PyTorch ecosystem.
Fix: pip install torch torchvision
AxiosError 403 / Upload Errors:
This usually occurs in hosted environments due to CORS policies. Locally, ensure you are running the latest version of Streamlit.
Fix: pip install --upgrade streamlit

ResourceBusy or Port Errors:
If port 8501 is already in use, Streamlit will suggest another port or you can specify one:
Fix: streamlit run app.py --server.port 8502