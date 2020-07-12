import random
import threading
import time
from typing import List, ClassVar, Dict, Type

import attr
import keyboard

_registry: Dict[str, Type['Action']] = {}


@attr.s(auto_attribs=True, slots=True)
class Action:
    """
    A single action, like pressing a key, waiting, etc. To define an actual action, you
    must subclass this and implement the run method. The 'args' will be as loaded from
    the configuration file.
    """
    kind: ClassVar[str]
    _args: List = attr.ib(factory=list)

    @classmethod
    def from_config(cls, config: Dict) -> 'Action':
        return _registry[config['kind']](args=config['args'])

    def run(self):
        raise NotImplementedError


class KeyPress(Action):
    kind = 'keypress'

    def run(self):
        key = self._args[0]
        if len(self._args) == 2:
            exec(f'keyboard.press("{key}")')
            time.sleep(float(self._args[1]))
            exec(f'keyboard.release("{key}")')
        else:
            exec(f'keyboard.send("{key}")')


class Wait(Action):
    kind = 'wait'

    def run(self):
        time.sleep(float(self._args[0]))


class Click(Action):
    kind = 'click'

    def run(self):
        button = self._args[0]
        if len(self._args) == 2:
            exec(f'mouse.press("{button}")')
            time.sleep(float(self._args[1]))
            exec(f'mouse.release("{button}")')
        else:
            exec(f'mouse.click("{button}")')


class WackyWasd(Action):
    kind = 'wackywasd'

    def run(self):
        wasd = list('wasd')
        new_wasd = []

        i = 0
        while not i == 4:
            print(i)
            print(wasd[i])
            temp = set(wasd)
            temp.remove(wasd[i])
            diff = [x for x in temp if x not in new_wasd]
            if i == 3 and len(diff) > 1:
                print("avoiding same final key")
                new_wasd.append(new_wasd[2])
                new_wasd[2] = wasd[3]
            else:
                new_wasd.append(random.choice(diff))
            i = i + 1

        print(wasd)
        print(new_wasd)
        for a, b in zip(wasd, new_wasd):
            exec(f'keyboard.remap_key("{a}", "{b}")')
            print(f'{a}: {b}')

        def reset():
            time.sleep(float(self._args[0]))
            keyboard.unhook_all()
        threading.Thread(target=reset).start()


for clz in Action.__subclasses__():
    _registry[clz.kind] = clz
