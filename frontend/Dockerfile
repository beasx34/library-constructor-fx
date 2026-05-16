FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# NEXT_PUBLIC_* переменные у Next.js встраиваются в бандл во время `next build`,
# поэтому пробрасываем URL бэкенда как build-arg.
ARG NEXT_PUBLIC_BASE_URL
ENV NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL}
RUN npm run build

FROM node:18-alpine AS prod
WORKDIR /app

# 1. Создаем только необходимые директории
RUN mkdir -p /app/public/picture && \
    chown -R node:node /app/public

USER node

COPY --from=builder --chown=node:node /app/package*.json ./
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/node_modules ./node_modules

ENV PORT=80
EXPOSE 80
CMD ["npm","run","start"]