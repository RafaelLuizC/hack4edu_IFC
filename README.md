<img width="100%" height="auto" alt="Desenho da Catarina e ao lado o título do projeto: Microaprendizagem supervisionada com metodologias ativas e IA" src="/images/banner.png" />


**Project Name: 
Microaprendizaje supervisado con metodologías activas e IA - Project**

**Description:**

This project builds an AI-powered microlearning ...

**Prerequisites:**

- Python 3.x ([https://www.python.org/downloads/](https://www.python.org/downloads/))
- Node.js and npm (or yarn) ([https://nodejs.org/](https://nodejs.org/))
- Git version control ([https://git-scm.com/](https://git-scm.com/))

**Installation:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Roshk01/Microlearning.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd micro_fastapi
   ```

3. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate  # Windows
   ```

4. **Install backend dependencies:**

   ```bash
   pip install fastapi uvicorn[standard] transformers[all]  # Additional dependencies for Hugging Face models
   ```

5. **Install frontend dependencies (assuming a React frontend):**

   ```bash
   cd ui-master  # Navigate to your frontend directory
   npm install  # or yarn install
   ```

**Running the Project:**

**1. Backend (API):**

   - **Start the development server:**

     ```bash
     uvicorn app:app --reload  # Adjust "app:app" if your app module is named differently
     ```

   - **Access the API:**

     Open http://localhost:8000/docs in your web browser to explore the API documentation (OpenAPI/Swagger).


