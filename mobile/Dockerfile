FROM node:22-alpine

RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++

WORKDIR /app

RUN corepack enable pnpm

# Copiar archivos de configuración del package
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias sin exigir lockfile congelado (el lock se genera en build)
RUN pnpm install --no-frozen-lockfile

# Copiar archivos de configuración
COPY vite.config.ts \
     tsconfig.json \
     tsconfig.node.json \
     tsconfig.app.json \
     tailwind.config.js \
     eslint.config.js \
     index.html \
     vercel.json ./

# Copiar código fuente
COPY src ./src
COPY public ./public
COPY dev-dist ./dev-dist

# Crear usuario
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8100

CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]
