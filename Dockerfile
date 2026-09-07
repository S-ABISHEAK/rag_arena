# Built for Hugging Face Spaces (Docker SDK) — see README.md's frontmatter
# and DEPLOYMENT.md for the full setup. Spaces expect the container to
# listen on port 7860 by convention, unlike Render's dynamic $PORT.
FROM python:3.12-slim

WORKDIR /app

# System deps for building any package that needs a C compiler at install
# time (some transitive scientific-stack wheels don't ship prebuilt for
# every platform) — kept minimal and removed from the final layer's apt
# cache to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/pdfs/ ./data/pdfs/

# Spaces run containers as a non-root user by default; pre-creating this
# with open permissions avoids a permission-denied surprise the first time
# the app writes an index file under data/sessions/<id>/.
RUN mkdir -p /app/data && chmod -R 777 /app/data

EXPOSE 7860

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
