# =============================================================================
# Stage 1: Dependencies — instala dependências
# =============================================================================
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copia apenas os arquivos de dependências (aproveita cache do Docker)
COPY package.json package-lock.json ./

# Instala dependências exatas do lockfile
RUN npm ci

# =============================================================================
# Stage 2: Builder — compila a aplicação
# =============================================================================
FROM node:20-alpine AS builder
WORKDIR /app

# Copia dependências do stage deps
COPY --from=deps /app/node_modules ./node_modules

# Copia código fonte
COPY . .

# Desativa telemetria durante o build
ENV NEXT_TELEMETRY_DISABLED 1

# Build da aplicação Next.js (gera os artefatos em .next/standalone e .next/static)
RUN npm run build

# =============================================================================
# Stage 3: Runner — imagem de produção
# =============================================================================
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Cria usuário não-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copia os artefatos compilados pelo Next.js no modo standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Troca para usuário não-root
USER nextjs

# Expõe porta e health check
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Inicia servidor Next.js standalone
CMD ["node", "server.js"]