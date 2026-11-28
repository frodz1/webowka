FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:2-alpine
LABEL org.opencontainers.image.source="https://github.com/frodz1/webowka"
# Port 8080 nie wymaga capability nadawanej przez obraz bazowy.
RUN setcap -r /usr/bin/caddy \
    && addgroup -S -g 10001 caddy \
    && adduser -S -D -H -u 10001 -G caddy caddy
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
USER caddy:caddy
EXPOSE 8080
