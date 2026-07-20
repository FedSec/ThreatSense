# apps/web/Dockerfile
# Next.js production multi-stage build

FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json ./
COPY package-lock.json* yarn.lock* pnpm-lock.yaml* ./

RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  else npm install; \
  fi

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Rewrites resolve API_INTERNAL_URL at build time (see next.config.js).
ARG API_INTERNAL_URL=http://api:8000
ARG NEXT_PUBLIC_API_BASE=/api
ENV API_INTERNAL_URL=$API_INTERNAL_URL
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm run build; \
  elif [ -f yarn.lock ]; then yarn build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
