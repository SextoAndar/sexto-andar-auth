# Auth Service API

Serviço FastAPI focado exclusivamente em autenticação: registro, login, logout e gerenciamento de sessão via JWT em cookies HTTP-only.

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose
- Python 3.8+

### 1. Clone e configure o ambiente

```bash
git clone <seu-repositorio>
cd sexto-andar-api

# Crie e ative um ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
```

### 2. Início simplificado (com migração automática)

```bash
# Subir tudo de uma vez - migração automática incluída!
docker-compose up --build -d
```

A migração será executada automaticamente antes da API iniciar.

### 2.1. Primeira instalação (alternativa manual)

Se preferir controle manual sobre as migrações:

```bash
# 1. Subir banco de dados
docker-compose up -d postgres

# 2. Executar migrações (manual)
python scripts/migrate_database.py

# 3. Subir toda aplicação
docker-compose up -d
```

### 3. Desenvolvimento contínuo

Para desenvolvimento normal, apenas execute:
```bash
docker-compose up
```

## 📖 Documentação da API

Após iniciar a aplicação, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🗄️ Gerenciamento do Banco de Dados

### Migração Automática

O Docker Compose agora executa migrações automaticamente:
- ✅ **Automático**: `docker-compose up` executa migração antes da API
- ✅ **Seguro**: Migração só executa se o banco estiver healthy
- ✅ **Limpo**: Container de migração para depois que completa
- ✅ **Confiável**: API só inicia após migração bem-sucedida

### Script de Migração

O script `scripts/migrate_database.py` é responsável por:
- Validar modelos do banco
- Aplicar migrações necessárias
- Criar/atualizar tabelas
- Verificar conectividade

#### Comandos do script:

```bash
# Executar migrações (interativo)
python scripts/migrate_database.py

# Executar migrações forçadas
python scripts/migrate_database.py --force

# Apenas verificar status
python scripts/migrate_database.py --check
```

### Quando executar migrações manualmente:

- ✅ **Desenvolvimento local** - Para debugar problemas de migração
- ✅ **Problemas específicos** - Se a migração automática falhar
- ✅ **Verificação** - Para conferir status antes de deployar

## 🏗️ Arquitetura

### Stack Tecnológico
- **Framework**: FastAPI com async/await
- **Banco de dados**: PostgreSQL com SQLAlchemy ORM
- **Autenticação**: JWT com HTTP-only cookies
- **Validação**: Pydantic models
- **Containerização**: Docker Compose

### Estrutura do Projeto

```
app/
├── controllers/          # Endpoints de autenticação
├── services/             # Lógica de autenticação
├── repositories/         # Acesso a dados (contas)
├── models/               # Modelos (apenas Account)
├── dtos/                 # DTOs de autenticação
├── database/             # Configuração do banco
└── main.py               # Aplicação principal

scripts/                  # Scripts utilitários
├── migrate_database.py   # Migração do banco (tabela accounts)
├── create_admin.py       # Criação de admin
└── README.md             # Documentação dos scripts
```

## 🔐 Autenticação

A API utiliza JWT com cookies HTTP-only seguros. Perfis suportados: `USER`, `PROPERTY_OWNER`, `ADMIN` (apenas para gestão de contas).

### Endpoints Principais
- `POST /api/v1/auth/register/user` - Registro de usuário
- `POST /api/v1/auth/register/property-owner` - Registro de proprietário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout

## 🛠️ Desenvolvimento

### Executar em modo desenvolvimento

```bash
# Com Docker
docker-compose up

# Ou diretamente com Python (após migração)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Após mudanças no modelo

```bash
# Simples: pare e suba novamente (migração automática)
docker-compose down
docker-compose up --build -d

# Ou, para controle manual:
docker-compose down
python scripts/migrate_database.py
docker-compose up -d
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### Configuração do pgAdmin

- **URL**: http://localhost:8080
- **Login Email**: admin@admin.com
- **Login Password**: admin

Para conectar ao PostgreSQL no pgAdmin:
- **Host**: postgres
- **Port**: 5432
- **Database**: sexto_andar_db
- **Username**: sexto_andar_user
- **Password**: sexto_andar_pass

## 📊 Monitoramento

### Health Checks
- `GET /` - Status básico da API
- `GET /health` - Status detalhado (API + banco)

### Logs
Os logs são configurados para stdout e incluem:
- Requests HTTP
- Erros de aplicação
- Status de migração
- Conectividade do banco

## 🐳 Docker

### Serviços disponíveis:
- **migrate**: Executa migrações automaticamente (roda uma vez e para)
- **api**: Aplicação FastAPI (porta 8000) - depende da migração
- **postgres**: PostgreSQL 15 (porta 5432)
- **pgadmin**: Interface web do PostgreSQL (porta 8080)

### Comandos úteis:

```bash
# Parar todos os serviços
docker-compose down

# Ver logs de um serviço
docker-compose logs api

# Reconstruir imagens
docker-compose build

# Executar apenas o banco
docker-compose up -d postgres
```

## ⚠️ Importante

1. **Migração automática**: `docker-compose up` cuida das migrações automaticamente
2. **Dependências corretas**: API só inicia após migração bem-sucedida
3. **Rebuilds**: Use `--build` após mudanças no código para recriar containers
4. **Admin users**: Crie usando `python scripts/create_admin.py` após subir os serviços

## 🤝 Contribuindo

1. Execute as migrações após fazer checkout
2. Teste suas mudanças localmente
3. Execute as migrações após mudanças no modelo
4. Documente novos endpoints na documentação OpenAPI

## 📞 Suporte

- **Documentação**: http://localhost:8000/docs
- **Issues**: Abra uma issue no repositório
- **Health Check**: http://localhost:8000/health
