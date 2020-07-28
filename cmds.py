import random
from typing import Dict, List, Union, Optional

import attr

from actions import Action
from special_types import Chatter

_registry: Dict[Union[int, str], 'Command'] = {}
_discounts: Dict[int, 'Command'] = {}


@attr.s(auto_attribs=True, slots=True, frozen=True)
class Command:
    name: str
    message: str
    cost: int
    discount: int
    _actions: List[Action] = attr.ib(factory=list)

    @classmethod
    def from_config(cls, config: Dict) -> 'Command':
        actions = []
        for cfg in config['actions']:
            actions.append(Action.from_config(cfg))
        return Command(
            config['name'],
            config['message'],
            config['cost'],
            config['discount'],
            actions,
        )

    def run(self, chat: Chatter):
        """
        Runs the command.
        :param chat: A function reference to send a message to chat.
        """
        print(f'running {self.name}')
        chat(self.message)
        for a in self._actions:
            a.run(chat)


def from_config(config: Dict) -> Dict[Union[str, int], Command]:
    """
    :param config: Parsed dictionary from YAML config load.
    :return: A dictionary of parsed commands keyed by the bits cost and discount cost.
        Meant for quick lookup in the bot message processing loop.
    """
    _registry.clear()
    _discounts.clear()
    for cfg in config['commands']:
        c = Command.from_config(cfg)
        if c.cost in _registry:
            raise ValueError(f'Bits cost conflict: {c.cost}')
        if c.discount in _discounts:
            raise ValueError(f'Discount conflict: {c.discount}')
        if c.name in _registry:
            raise ValueError(f'Command name conflict: {c.name}')
        _registry[c.cost] = c
        _discounts[c.discount] = c
        _registry[c.name] = c
    print(_registry)
    return _registry


def run(x: Union[str, int], chat: Chatter, discount: bool = False) -> Command:
    """
    Runs a command. If the input is a string, it'll do a lookup based on the name. If
    it's an integer, it'll do a lookup based on bits/discount cost.
    :param x: Lookup value or string. If a number, looks up the command associated with
        the bits cost. If a string, looks up the command name.
    :param discount: Whether to match bits amounts to discounted values.
    :param chat: A function reference to send a message to chat.
    :returns: The called command, if one was found. Else None.
    """
    if discount:
        cmd = _discounts.get(x)
    else:
        cmd = _registry.get(x)
    if cmd is not None:
        cmd.run(chat)
    elif isinstance(x, str):  # When a command name was passed, we warn if nothing was found
        print(f'WARNING: command not found! {x}')
    return cmd


def run_nth(i: int, chat: Chatter) -> Optional[Command]:
    """ Runs the nth command. Used during stream setup/testing. """
    # Double it because we're adding the commands multiple times for faster lookups
    i *= 2
    if not (0 <= i < len(_registry)):
        print('COMMAND NUMBER EXCEEDS THE MAX')
        return None
    cmd = list(_registry.values())[i]
    cmd.run(chat)
    return cmd


def run_random(chat: Chatter) -> Command:
    """ Runs a random command. Returns the command. """
    cmd = random.choice(list(_registry.values()))
    cmd.run(chat)
    return cmd
