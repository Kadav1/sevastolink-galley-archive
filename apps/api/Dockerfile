FROM python:3.12-slim

# WORKDIR mirrors the volume-mounted repo path so settings.py parents[4] resolves correctly.
# The full repo is mounted at /repo at runtime; this matches the path used by settings.py.
WORKDIR /repo/apps/api

# Install packages/shared-prompts — the build context is the repo root so this
# path is available at build time.  The package is also present at runtime via
# the volume mount, but pip-installing it here means the import works even
# without a mount (e.g. in CI or standalone container use).
COPY packages/shared-prompts /build/shared-prompts
RUN pip install --no-cache-dir /build/shared-prompts

# Install API Python dependencies — layer cached unless pyproject.toml changes.
COPY apps/api/pyproject.toml ./
RUN pip install --no-cache-dir -e "."

RUN addgroup --system galley && adduser --system --ingroup galley galley
USER galley

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
