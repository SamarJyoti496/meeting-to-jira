🎤 Meeting to Jira System 🚀
Stop taking meeting notes. Start creating tickets. Automatically.

This project is a full-stack application that transforms meeting recordings into actionable Jira tickets. It uses AI to transcribe audio, extract requirements, and create tasks, bugs, and stories directly in your Jira project, streamlining your workflow and ensuring no action item gets lost.

(A GIF showing the file upload, progress, and ticket creation would be perfect here)

✨ About The Project
In fast-paced development cycles, crucial decisions and action items discussed in meetings can easily be forgotten or lost in translation. This tool was built to solve that problem by creating a seamless bridge between conversation and execution.

Simply upload a meeting recording (MP3, WAV, MP4, etc.), and the system will:

Transcribe the entire conversation using a self-hosted Whisper model for privacy and cost-effectiveness.

Analyze the transcription using the Gemini AI API to intelligently identify and extract software requirements, tasks, and bugs.

Create well-structured tickets in your specified Jira project, complete with summaries, descriptions, and acceptance criteria.

This frees up developers and project managers from manual note-taking, allowing them to focus on what truly matters: building great software.

🚀 Features
Seamless File Upload: A modern, drag-and-drop interface for uploading meeting recordings.

Self-Hosted Transcription: Uses faster-whisper for fast, private, and free audio-to-text conversion.

AI-Powered Requirement Extraction: Leverages the Gemini API to understand the transcription and pull out actionable items.

Automatic Jira Ticket Creation: Creates tickets in Jira with pre-filled summaries, descriptions, and labels.

Real-Time Progress Tracking: The frontend polls the backend to show the user the live status of the transcription and ticket creation process.

Scalable Backend: Built with FastAPI for high performance and asynchronous request handling.

Modern Frontend: A responsive and beautiful UI built with Vite, React, and Tailwind CSS.

Containerized for Easy Deployment: Fully containerized with Docker and NGINX for consistent and simple deployment.

Database Migrations: Uses Alembic to manage database schema changes safely.

Installation
Clone the repository:

cd meeting-to-jira

Set up the environment configuration:

Copy the example environment file.

cp .env.example .env

Open the .env file and fill in your credentials for:

DATABASE_URL (e.g., your Neon DB connection string)

GOOGLE_API_KEY

JIRA_SERVER, JIRA_EMAIL, and JIRA_API_TOKEN

Set up the Python backend:

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate # On Windows use `.venv\Scripts\activate`

Install backend dependencies:

pip install -r requirements.txt

Set up the database:

Run the Alembic migrations to create the database tables.

alembic upgrade head

Set up the React frontend:

Navigate to the frontend directory:

cd frontend

Install frontend dependencies:

npm install

Return to the root directory:

cd ..

Running the Application
Start the backend server:

From the root directory, run:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Start the frontend development server:

In a new terminal, navigate to the frontend directory and run:

cd frontend
npm run dev

The application should now be running!

Backend API available at http://localhost:8000

Frontend accessible at http://localhost:3000

🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📧 Contact
[Samar ] - [https://www.linkedin.com/in/samarjyoti-kalita-424b42190/] - [samarjyoti496@gmail.com] - [https://x.com/samarjyoti496]
