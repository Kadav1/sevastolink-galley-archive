FROM node:22-slim

# WORKDIR mirrors the volume-mounted repo path
WORKDIR /repo/apps/web

# Install dependencies before source is mounted — cached unless package.json changes
COPY package*.json ./
RUN npm install

RUN addgroup --system galley && adduser --system --ingroup galley galley
USER galley

EXPOSE 3000

# --host 0.0.0.0 binds to all interfaces so the port is reachable from outside the container
CMD ["npx", "vite", "--host", "0.0.0.0"]
