FROM node:22-slim

WORKDIR /app
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY apps/web .
CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]
