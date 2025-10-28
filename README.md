# Auth Service API

Serviço FastAPI focado exclusivamente em autenticação: registro, login, logout e gerenciamento de sessão via JWT em cookies HTTP-only.

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose
- Python 3.8+

### 1. Clone e configure o ambiente

```bash
git clone <seu-repositorio>
cd sexto-andar-auth

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
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

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
- **Hash de Senha**: bcrypt
- **Containerização**: Docker Compose

## �‍💼 Gerenciamento de Admins

### Criar Primeiro Admin (Bootstrap)

Após iniciar os containers, crie o primeiro admin:

```bash
docker exec sexto-andar-auth python scripts/create_admin.py <username> "<full_name>" <email> <password> <phone>
```

**Exemplo:**
```bash
docker exec sexto-andar-auth python scripts/create_admin.py admin "Admin User" admin@example.com "@Admin11" 11999999999
```

**Validações:**
- Username: 3-50 caracteres (apenas letras, números e underscore)
- Email: formato válido e único
- Senha: mínimo 8 caracteres
- Telefone: 10-15 dígitos

**Saída esperada:**
```
✅ Admin user created successfully!

👤 Admin Details:
   ID: uuid-aqui
   Username: admin
   Full Name: Admin User
   Email: admin@example.com
   Role: Administrator
   Created: 2025-10-28 06:35:22

🎉 You can now login with these credentials!
```

### Criar Admins Adicionais via API

Após ter um admin, crie novos admins via endpoint protegido:

```bash
# 1. Faça login como admin
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "@Admin11"
  }' \
  -c cookies.txt

# 2. Crie novo admin (requer autenticação)
curl -X POST http://localhost:8001/api/v1/auth/admin/create-admin \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "username": "admin2",
    "fullName": "Segundo Admin",
    "email": "admin2@example.com",
    "phoneNumber": "11988776655",
    "password": "senha123456"
  }'
```

### Deletar Admins via API

Apenas admins autenticados podem deletar outros admins (não podem deletar a si mesmos ou o último admin):

```bash
curl -X DELETE http://localhost:8001/api/v1/auth/admin/delete-admin/{admin_id} \
  -b cookies.txt
```

---

##  Autenticação

### Fluxo de Login
1. Cliente faz `POST /api/v1/auth/login` com username e password
2. API valida credenciais contra o banco (bcrypt)
3. API gera JWT com claims: `sub` (user_id), `username`, `role`
4. JWT é retornado no response e em um HTTP-only cookie
5. Cliente envia JWT em requisições subsequentes
6. API valida JWT localmente (sem chamar banco)

### Roles Disponíveis
- **USER**: Usuário comum (registra via `/register/user`)
- **PROPERTY_OWNER**: Proprietário de imóvel (registra via `/register/property-owner`)
- **ADMIN**: Administrador do sistema (criado apenas via script ou API protegida)

### Endpoints de Autenticação
- `POST /api/v1/auth/register/user` - Registrar usuário
- `POST /api/v1/auth/register/property-owner` - Registrar proprietário
- `POST /api/v1/auth/login` - Login (retorna JWT)
- `POST /api/v1/auth/logout` - Logout (limpa cookie)
- `GET /api/v1/auth/me` - Obter usuário autenticado
- `POST /api/v1/auth/introspect` - Validar token (service-to-service)
- `POST /api/v1/auth/admin/create-admin` - Criar admin (admin only)
- `DELETE /api/v1/auth/admin/delete-admin/{id}` - Deletar admin (admin only)

### Segurança
- ✅ JWT com expiração (30 minutos)
- ✅ HTTP-only cookies (proteção contra XSS)
- ✅ SameSite=Lax (proteção contra CSRF)
- ✅ Hash bcrypt de senhas
- ✅ Validação de autorização por role
- ✅ Logs de auditoria (criação/deleção de admin)
- ⚠️ Em produção: ativar HTTPS (`secure=True` no cookie)

## � Exemplos de Uso

### Registrar novo usuário

```bash
curl -X POST http://localhost:8001/api/v1/auth/register/user \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao_silva",
    "fullName": "João Silva",
    "email": "joao@example.com",
    "phoneNumber": "11987654321",
    "password": "senha123456"
  }'
```

**Resposta (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao_silva",
  "fullName": "João Silva",
  "email": "joao@example.com",
  "role": "USER",
  "created_at": "2025-10-28T10:30:00"
}
```

### Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao_silva",
    "password": "senha123456"
  }' \
  -c cookies.txt  # Salva o cookie
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "joao_silva",
    "role": "USER"
  }
}
```

### Obter dados do usuário autenticado

```bash
curl http://localhost:8001/api/v1/auth/me \
  -b cookies.txt  # Usa o cookie do login
```

**Resposta (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao_silva",
  "fullName": "João Silva",
  "email": "joao@example.com",
  "role": "USER",
  "created_at": "2025-10-28T10:30:00"
}
```

### Logout

```bash
curl -X POST http://localhost:8001/api/v1/auth/logout \
  -b cookies.txt
```

### Validar token (service-to-service)

```bash
curl -X POST http://localhost:8001/api/v1/auth/introspect \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Resposta (200):**
```json
{
  "active": true,
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao_silva",
  "role": "USER",
  "exp": 1635345600
}
```

### Criar novo admin (como admin autenticado)

```bash
# 1. Faça login como admin (se houver cookie previamente)
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "@Admin11"
  }' \
  -c cookies.txt

# 2. Crie novo admin
curl -X POST http://localhost:8001/api/v1/auth/admin/create-admin \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "username": "admin2",
    "fullName": "Segundo Admin",
    "email": "admin2@example.com",
    "phoneNumber": "11988776655",
    "password": "senha123456"
  }'
```

**Resposta (201):**
```json
{
  "id": "660f9511-f40c-52e5-b827-557766551111",
  "username": "admin2",
  "fullName": "Segundo Admin",
  "email": "admin2@example.com",
  "role": "ADMIN",
  "created_at": "2025-10-28T10:35:00"
}
```

### Deletar admin (como admin autenticado)

```bash
curl -X DELETE http://localhost:8001/api/v1/auth/admin/delete-admin/660f9511-f40c-52e5-b827-557766551111 \
  -b cookies.txt
```

**Resposta (200):**
```json
{
  "message": "Admin deleted successfully"
}
```

## ⚠️ Status Codes e Erros

### Sucesso
- **200 OK**: Requisição bem-sucedida (GET, POST logout, DELETE bem-sucedido)
- **201 Created**: Recurso criado (POST register, POST login, POST create-admin)

### Erros de Cliente
- **400 Bad Request**: 
  - Validação falhou (username inválido, email malformado, etc)
  - Credenciais inválidas (username/password incorreto)
  - Operação não permitida (tentar deletar último admin, deletar a si mesmo, etc)
- **401 Unauthorized**: 
  - Token ausente, inválido ou expirado
  - Não autenticado para acessar recurso
- **403 Forbidden**: 
  - Autenticado mas sem permissão (ex: usuário tentando criar admin)
- **404 Not Found**: 
  - Recurso não encontrado (ex: admin ID inválido no delete)
- **409 Conflict**: 
  - Email já existe
  - Username já existe

### Erros de Servidor
- **500 Internal Server Error**: Erro inesperado no servidor
- **503 Service Unavailable**: Banco de dados indisponível

### Exemplo de Erro

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_inexistente",
    "password": "senha123456"
  }'
```

**Resposta (400):**
```json
{
  "detail": "Invalid username or password"
}
```

## �️ Desenvolvimento

### Executar em modo desenvolvimento

```bash
# Com Docker
docker-compose up

# Ou diretamente com Python (após migração)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
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

## Configuração

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
- **auth**: Aplicação FastAPI (porta 8001) - depende da migração
- **postgres**: PostgreSQL 15 (porta 5432)
- **pgadmin**: Interface web do PostgreSQL (porta 8080)

### Comandos úteis:

```bash
# Parar todos os serviços
docker-compose down

# Ver logs de um serviço
docker-compose logs auth

# Reconstruir imagens
docker-compose build

# Executar apenas o banco
docker-compose up -d postgres

# Criar admin
docker exec sexto-andar-auth python scripts/create_admin.py admin "Admin User" admin@example.com "@Admin11" 11999999999
```

## ⚠️ Importante

1. **Migração automática**: `docker-compose up` cuida das migrações automaticamente
2. **Dependências corretas**: API só inicia após migração bem-sucedida
3. **Rebuilds**: Use `--build` após mudanças no código para recriar containers
4. **Admin users**: Crie usando `python scripts/create_admin.py` após subir os serviços

## 🔗 Integração com Outros Serviços

### Validação de Token em Serviço Externo

Qualquer serviço pode validar tokens gerados por esta API usando duas estratégias:

#### 1. Validação Local (Recomendado para performance)
Se seu serviço tiver acesso a `SECRET_KEY` (mesma chave usada aqui):

```python
import jwt
from datetime import datetime

SECRET_KEY = "sua-chave-secreta"
ALGORITHM = "HS256"

def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expirado"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token inválido"}
```

#### 2. Validação Remota via Endpoint

```bash
# No seu serviço
curl -X POST http://auth-service:8001/api/v1/auth/introspect \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

### Exemplo: FastAPI com Validação

```python
from fastapi import FastAPI, Depends, HTTPException
import httpx

app = FastAPI()
AUTH_SERVICE_URL = "http://localhost:8001"

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/introspect",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(401, "Invalid token")
        return response.json()

@app.get("/protected")
async def protected_route(token_info = Depends(verify_token)):
    return {"message": f"Hello {token_info['username']}"}
```

## 🛠️ Troubleshooting

### API não inicia após `docker-compose up`

**Sintoma**: Container auth em restart contínuo
**Solução**:
```bash
# 1. Verifique logs
docker-compose logs auth

# 2. Limpe tudo e reinicie
docker-compose down -v
docker system prune -a --volumes -f
docker-compose up --build -d
```

### Erro: "Cannot GET /health"

**Sintoma**: Health check falha
**Solução**: 
- Verifique se porta 8001 está correta em docker-compose.yml
- Confirme que API iniciou: `docker-compose logs auth | grep "Uvicorn running"`

### Erro: "database connection refused"

**Sintoma**: API não consegue conectar ao PostgreSQL
**Solução**:
```bash
# 1. Verifique se postgres está rodando
docker-compose ps postgres

# 2. Verifique DATABASE_URL
docker-compose exec auth env | grep DATABASE_URL

# 3. Tente reconectar
docker-compose restart auth
```

### Admin script falha: "ModuleNotFoundError"

**Sintoma**: Erro ao executar `docker exec sexto-andar-auth python scripts/create_admin.py`
**Solução**:
- Verifique se Dockerfile tem `COPY scripts/ ./scripts/`
- Reconstrua: `docker-compose build --no-cache`

### Erro 409 Conflict ao criar usuário

**Sintoma**: "Email already exists" ou "Username already taken"
**Solução**: Use username/email diferentes ou delete usuário do banco:
```bash
docker exec -it postgres-container-id psql -U sexto_andar_user -d sexto_andar_db
DELETE FROM accounts WHERE username = 'usuario_duplicado';
```

### Token inválido ou expirado

**Sintoma**: Erro 401 em endpoints protegidos
**Solução**:
- Faça login novamente para obter novo token
- Verifique se JWT_EXPIRE_MINUTES está correto (padrão: 30 minutos)
- Confirme que `SECRET_KEY` é a mesma em todos os serviços

### Migração do banco falha

**Sintoma**: Container migrate com status "exited"
**Solução**:
```bash
# 1. Verifique o erro
docker-compose logs migrate

# 2. Execute migração manualmente
docker-compose exec auth python scripts/migrate_database.py --force

# 3. Recrie tudo
docker-compose down -v
docker-compose up --build -d
```

## 🤝 Contribuindo

1. Execute as migrações após fazer checkout
2. Teste suas mudanças localmente com `docker-compose up`
3. Execute as migrações após mudanças no modelo
4. Documente novos endpoints na documentação OpenAPI
5. Mantenha a consistência de naming (em inglês na código, em português em comentários/docs)

### Boas Práticas
- ✅ Sempre validar input com Pydantic
- ✅ Usar dependências FastAPI para autenticação
- ✅ Logar operações sensíveis (criação/deleção de admin)
- ✅ Implementar proteções contra edge cases
- ✅ Testar endpoints via Swagger UI (/docs) antes de commitar

## 📞 Suporte

- **Documentação API**: http://localhost:8001/docs
- **Swagger UI**: http://localhost:8001/swagger.json
- **Health Check**: http://localhost:8001/health
- **Issues**: Abra uma issue no repositório
- **pgAdmin**: http://localhost:8080 (para debugging do banco)
