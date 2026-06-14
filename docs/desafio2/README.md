# 🐳 Desafio 2 — CI/CD do Backend e Frontend (CondoCombat)

## 🎯 Objetivo

Criar uma pipeline de **Integração Contínua (CI)** para o **Backend (FastAPI)** e o **Frontend (Next.js)** do CondoCombat. Diferente do Desafio 1, aqui não há deploy — a pipeline termina no push das imagens Docker para o DockerHub.

A pipeline deve executar **4 etapas** para cada aplicação:

1. **Lint** — verificação de estilo e qualidade de código
2. **Testes** — execução dos testes automatizados
3. **Build Docker** — construção da imagem Docker
4. **Push** — envio da imagem para o DockerHub

| Aplicação | Stack | Porta | Testes |
|-----------|-------|-------|--------|
| 🏗️ Backend | FastAPI + Python 3.12 | 8000 | pytest-asyncio (216 testes) |
| 🎨 Frontend | Next.js 14 + TypeScript strict | 3000 | Vitest + Testing Library (79 testes) |

## ⚠️ Aviso

**Não há etapa de deploy.** A pipeline termina no push das imagens para o DockerHub. Os `Dockerfile` e `docker-compose.yml` serão criados por você seguindo os guias nos arquivos específicos de cada plataforma.

Escolha a plataforma desejada abaixo:

| Plataforma | Arquivo |
|-----------|---------|
| 🐙 GitHub Actions | [`README.github.md`](./README.github.md) |
| 🦊 GitLab CI/CD | [`README.gitlab.md`](./README.gitlab.md) |

---

## 📚 Referências

- [DockerHub — Repositórios](https://hub.docker.com/)
- [Docker — Boas práticas para Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [FastAPI — Implantação com Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js — Implantação com Docker](https://nextjs.org/docs/pages/building-your-application/deploying#docker-image)
- [GitHub Actions — Documentação](https://docs.github.com/en/actions)
- [GitLab CI/CD — Documentação](https://docs.gitlab.com/ee/ci/)
- [CondoCombat — Backend](../../backend/)
- [CondoCombat — Frontend](../../frontend/)
