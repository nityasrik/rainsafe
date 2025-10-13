# backend/Dockerfile

FROM python:3.11

WORKDIR /app

COPY requirements.txt .

# Layer 1: Install Python packages from requirements
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: Download the spaCy NLP model
RUN python -m spacy validate || true
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]