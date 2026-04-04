FROM python:3.12-slim

# WORKDIR mirrors the volume-mounted repo path so settings.py parents[4] resolves correctly.
# The full repo is mounted at /repo at runtime; this matches the path used by settings.py.
WORKDIR /repo/apps/api

# Install dependencies before source is mounted — cached unless pyproject.toml changes
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "."

RUN addgroup --system galley && adduser --system --ingroup galley galley
USER galley

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
