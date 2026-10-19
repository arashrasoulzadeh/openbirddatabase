# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
# node_modules is installed into a normal image layer (a cache mount is not kept when CI reuses this layer, which left
# the build step without `next`). Only npm's download cache is a BuildKit cache mount, so changed dependencies are
# reinstalled quickly; with unchanged package*.json this whole layer is reused (clear: docker builder prune).
RUN --mount=type=cache,target=/root/.npm \
    npm install --prefer-offline --no-audit --no-fund
COPY . .
# Public URLs are baked into the client bundle at build time
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SITE_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL \
    NEXT_TELEMETRY_DISABLED=1
# .next/cache speeds up repeated Next.js compiles
RUN --mount=type=cache,target=/app/.next/cache \
    mkdir -p public && npm run build

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
