Catalyst Talent Engine: AI-Powered Scouting and Engagement

Live Production URL: https://huggingface.co/spaces/nithyaapriyaa/talent-scout

Project Overview:
Built for the Catalyst Hackathon, this AI agent automates the end-to-end recruitment funnel. The system parses Job Descriptions, mathematically ranks candidates using semantic embeddings, and performs simulated conversational outreach to assess candidate interest.

System Logic and Scoring:
The platform utilizes a dual-engine scoring approach to ensure both technical accuracy and qualitative evaluation:
1. Match Score (50%)
Semantic Search: Utilizes all-MiniLM-L6-v2 vector embeddings to identify conceptual matches between resumes and job descriptions.
Hybrid Search Override: Includes direct keyword-matching logic for specific identifiers to ensure high precision on targeted searches.
Data Validation: Automatically filters "Bad Data," such as blank documents or non-resume PDF files.

2. Interest Score (50%)
Agentic Engagement: Powered by a Groq LLM (llama-3.1-8b-instant), the system simulates a recruitment conversation based on the candidate’s specific career history.
Simulated Transcript: Generates a dialogue sequence to gauge potential interest levels and fit.

Testing Suite
A curated testing_batch directory is included to demonstrate system robustness:
blank_pdfs: Verifies the system’s ability to skip unreadable or empty files.
random_pdfs: Validates the audit logic that identifies and flags non-resume documents.
actual_resumes: Demonstrates the core evaluation and outreach pipeline using valid candidate data.

Local Setup
For technical documentation and instructions on how to run this engine in a local environment, please refer to LOCAL_SETUP.md.