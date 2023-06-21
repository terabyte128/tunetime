FROM node:16-alpine AS builder

WORKDIR /app

COPY ./tunetime-ui/package.json ./tunetime-ui/yarn.lock ./
RUN yarn

COPY ./tunetime-ui/ ./
RUN yarn build

FROM caddy
COPY --from=builder /app/dist/ /usr/share/caddy/
COPY ./Caddyfile /etc/caddy/Caddyfile


