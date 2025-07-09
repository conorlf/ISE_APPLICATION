 StataGO
A modern web application for econometric data processing and analysis that automates data harmonization and generates publication-ready Stata .do files for econometric research.
## 🎯 Overview

StataGo is a comprehensive tool designed for economists and researchers to streamline their data analysis workflow. The application combines AI-powered data harmonization with automated econometric code generation, making it easier to process datasets and conduct rigorous econometric analysis.

### Key Features

- **AI-Powered Data Harmonization**: Automatically clean, standardize, and merge multiple datasets
- **Smart Column Mapping**: Intelligent matching of column headers across different data sources
- **Stata Code Generation**: Automatically generate .do files for various econometric models
- **Multiple Regression Types**: Support for OLS, IV, Fixed Effects, Logit, and Probit models
- **Data Preview**: Interactive preview of cleaned datasets before analysis
- **Duplicate Detection**: Identify and handle duplicate records across datasets
- **Export Functionality**: Download cleaned CSV files and generated Stata code

## 🛠 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for modern, responsive styling
- **Lucide React** for consistent iconography
- **React Router** for navigation

### Backend
- **Flask** (Python) for the REST API
- **Pandas** for data manipulation and analysis
- **OpenAI API** for intelligent data processing
- **Flask-CORS** for cross-origin resource sharing

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn** package manager
- **OpenAI API Key** (optional, for AI features)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Project
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd econ-file-factory
npm install
```

### 3. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd econ-file-factory/backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
# Install Python dependencies
pip install -r requirements.txt
``
### 4. Environment Configuration

Create a `.env` file in the `econ-file-factory/backend` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_DEBUG=True
```
**Note**: The OpenAI API key is optional. The application can run without it, but AI-powered features will be disabled.
## 🏃‍♂️ Running the Application
### Start the Backend Server

```bash
cd econ-file-factory/backend
python app.py
```

The Flask server will start on `http://localhost:5000`

### Start the Frontend Development Server

In a new terminal:

```bash
cd econ-file-factory
npm run dev
```
The React server will start on `http://localhost:5000'


### Access the Application

Open your browser and navigate to `http://localhost:5173` to use the application.
