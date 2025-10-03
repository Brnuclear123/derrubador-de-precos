from pywebpush import webpush, WebPushException
from ..core.settings import settings
from ..core.logger import logger


def send_webpush(subscription_info: dict, payload: dict):
    try:
        webpush(
            subscription_info=subscription_info,
            data=str(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_CLAIMS_SUB},
        )
        logger.info({"event": "webpush_sent"})
    except WebPushException as ex:
        logger.error({"event": "webpush_error", "error": str(ex)})
