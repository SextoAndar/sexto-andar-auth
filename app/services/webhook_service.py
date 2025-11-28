"""
Service for sending notifications to external webhooks.
"""
import logging
import httpx
from uuid import UUID

# Configure logger
logger = logging.getLogger(__name__)

# Hardcoded webhook URL as per user's instruction
WEBHOOK_URL = "https://sexto-andar-api-3ef30ad16a1f.herokuapp.com/api/internal/user-deleted-webhook"

# Placeholder for the internal API secret.
# In a real-world scenario, this MUST be loaded from a secure environment variable.
INTERNAL_API_SECRET = "your-internal-api-secret-placeholder"


class WebhookService:
    """
    Handles sending webhook notifications for inter-service communication.
    """

    @staticmethod
    async def send_user_deleted_webhook(user_id: UUID):
        """
        Notifies the external API that a user has been deleted.

        This sends a POST request to the WEBHOOK_URL.

        Args:
            user_id: The UUID of the user who was deleted.
        """
        if not WEBHOOK_URL or not INTERNAL_API_SECRET:
            logger.warning(
                "WEBHOOK_URL or INTERNAL_API_SECRET is not configured. "
                "Skipping webhook call."
            )
            return

        headers = {
            "X-Internal-Secret": INTERNAL_API_SECRET
        }
        payload = {
            "user_id": str(user_id)
        }

        logger.info(f"Sending user deletion webhook for user_id: {user_id} to {WEBHOOK_URL}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(WEBHOOK_URL, json=payload, headers=headers)

                # Check if the request was successful
                if 200 <= response.status_code < 300:
                    logger.info(
                        "Successfully sent user deletion webhook. "
                        f"Response: {response.status_code}"
                    )
                else:
                    logger.error(
                        f"Failed to send user deletion webhook for user_id: {user_id}. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                # Raise an exception for client-side errors or server-side errors
                response.raise_for_status()

        except httpx.RequestError as e:
            logger.critical(
                f"An error occurred while sending the user deletion webhook for user_id: {user_id}. "
                f"Error: {e}"
            )
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during the user deletion webhook for user_id: {user_id}. "
                f"Error: {e}"
            )

# Create a singleton instance
webhook_service = WebhookService()
