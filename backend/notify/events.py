import redis
import logging
import json

from tsg import settings

NOTIFY_CHANNEL_NAME = "TSG_NOTIFY"

logger = logging.getLogger(__name__)

r = redis.Redis.from_url(settings.REDIS_URL)


class Event:
    """
    An event which is meant to be sent to a user via websocket
    """

    def __init__(self, user_id: int, typ: str, msg: str):
        self.user_id = user_id
        self.typ = typ
        self.msg = msg

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)


def store_event(event: Event) -> None:
    """
    Stores an event in the redis database.

    The stored event then gets consumed by the go worker who proceeds to send
    the event to the user via a websocket connection if the user is connected.
    """

    if isinstance(event, Event) is False:
        logger.error(f"Can only save objects of typ {Event.__class__}. Object was of class {event.__class__}")
        return
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        logger.error("Could not connect with redis!")
        return

    if not r.lpush(NOTIFY_CHANNEL_NAME, event.to_json()):
        logger.error(f"Failed to push {event} to {NOTIFY_CHANNEL_NAME} queue!")
