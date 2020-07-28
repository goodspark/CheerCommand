""" Special types to reduce type annotation clutter. """
from typing import Callable

# A callable function reference that will send a message to chat.
Chatter = Callable[[str], None]
