# Scripts

Esta pasta contém scripts utilitários para o projeto Real Estate Management API.

## migrate_database.py

Script para migração e inicialização do banco de dados.

### Uso:

```bash
# Executar migrações (interativo)
python scripts/migrate_database.py

# Executar migrações forçadas (sem confirmação)
python scripts/migrate_database.py --force

# Apenas verificar status do banco
python scripts/migrate_database.py --check
```

### Quando usar:
- **Primeira instalação**: Execute antes de iniciar a aplicação pela primeira vez
- **Após mudanças no modelo**: Execute sempre que modificar os modelos do banco
- **Problemas de sincronização**: Execute quando o banco estiver desatualizado

### O que o script faz:
1. Valida os modelos SQLAlchemy
2. Aplica migrações necessárias
3. Cria/atualiza tabelas
4. Verifica conectividade do banco

## create_admin.py

Script para criar usuários administradores.

### Uso:

```bash
# Criar um usuário admin
python scripts/create_admin.py
```

### Quando usar:
- Para criar o primeiro usuário administrador
- Para criar novos administradores do sistema

## Ordem de execução recomendada:

1. **Uso normal (automático):**
   ```bash
   # Migração automática no Docker Compose
   docker-compose up --build -d
   
   # Criar admin se necessário
   python scripts/create_admin.py
   ```

2. **Primeira instalação (controle manual):**
   ```bash
   # 1. Subir o banco com Docker
   docker-compose up -d postgres
   
   # 2. Executar migrações manualmente
   python scripts/migrate_database.py
   
   # 3. Criar admin (opcional)
   python scripts/create_admin.py
   
   # 4. Iniciar a aplicação
   docker-compose up -d api
   ```

## Notas importantes:

- ✅ **Migração automática**: Docker Compose executa `migrate_database.py` automaticamente
- ✅ **Sem intervenção manual**: `docker-compose up` cuida de tudo
- ✅ **Scripts disponíveis**: Para casos especiais e debugging
- ✅ **Ordem garantida**: API só inicia após migração bem-sucedida
- ⚠️ **Use `--build`**: Para aplicar mudanças no código após modificações
