# app/services/property_relation_service.py
"""
Service for validating user-property relations
Communicates with the properties API to check if a user has interactions with an owner's properties
"""

import httpx
from uuid import UUID
import logging

from app.settings import settings

logger = logging.getLogger(__name__)


async def check_user_property_relation(user_id: UUID, owner_id: UUID) -> bool:
    """
    Verifica se o usuário tem relação (visita/proposta) com propriedades do owner.
    
    Faz chamada ao endpoint interno da API de imóveis para validar se existe
    relação entre o usuário e as propriedades do proprietário.
    
    Args:
        user_id: ID do usuário a ser verificado
        owner_id: ID do proprietário
    
    Returns:
        True se existe relação (visita ou proposta), False caso contrário
        
    Security:
        - Usa INTERNAL_API_SECRET para autenticação entre serviços
        - Fail-safe: retorna False em caso de erro (nega acesso por padrão)
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.PROPERTIES_API_URL}/api/internal/check-user-property-relation",
                params={
                    "user_id": str(user_id),
                    "owner_id": str(owner_id)
                },
                headers={
                    "X-Internal-Secret": settings.INTERNAL_API_SECRET
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                has_relation = data.get("has_relation", False)
                
                # Log para auditoria
                if has_relation:
                    logger.info(
                        f"User {user_id} has relation with owner {owner_id} "
                        f"(visits: {data.get('has_visit', False)}, "
                        f"proposals: {data.get('has_proposal', False)})"
                    )
                else:
                    logger.info(f"User {user_id} has NO relation with owner {owner_id}")
                
                return has_relation
            
            elif response.status_code == 401:
                logger.error("Invalid INTERNAL_API_SECRET - inter-service authentication failed")
                return False
            
            elif response.status_code == 404:
                logger.warning("Properties API endpoint not found (404)")
                return False
            
            else:
                logger.error(f"Properties API returned unexpected status {response.status_code}")
                return False
    
    except httpx.TimeoutException:
        logger.error(
            f"Timeout connecting to properties API at {settings.PROPERTIES_API_URL} "
            f"(user_id={user_id}, owner_id={owner_id})"
        )
        return False
    
    except httpx.RequestError as e:
        logger.error(
            f"Error connecting to properties API: {e} "
            f"(user_id={user_id}, owner_id={owner_id})"
        )
        return False
    
    except Exception as e:
        logger.error(
            f"Unexpected error checking user-property relation: {e} "
            f"(user_id={user_id}, owner_id={owner_id})"
        )
        return False
