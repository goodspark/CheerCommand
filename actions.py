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

    Subclasses can optionally override 'validate' to do post-config-load validation or
    any other processing (like converting args to types and fields).
    """
    kind: ClassVar[str]
    _args: List = attr.ib(factory=list)

    @classmethod
    def from_config(cls, config: Dict) -> 'Action':
        a = _registry[config['kind']](args=config['args'])
        a.validate()
        return a

    def validate(self):
        pass

    def run(self):
        raise NotImplementedError


class KeyPress(Action):
    kind = 'keypress'
    key: str = ''
    duration_s: float = 0

    def validate(self):
        self.key = str(self._args[0])
        if len(self._args) == 2:
            self.duration_s = float(self._args[1])

    def run(self):
        if self.duration_s > 0:
            exec(f'keyboard.press("{self.key}")')
            time.sleep(self.duration_s)
            exec(f'keyboard.release("{self.key}")')
        else:
            exec(f'keyboard.send("{self.key}")')


class Wait(Action):
    kind = 'wait'
    duration_s: float = 0.0

    def validate(self):
        self.duration_s = float(self._args[0])

    def run(self):
        time.sleep(self.duration_s)


class Click(Action):
    kind = 'click'
    button: str = ''
    duration_s: float = 0.0

    def validate(self):
        self.button = self._args[0]
        if len(self._args) == 2:
            self.duration_s = float(self._args[1])

    def run(self):
        if self.duration_s > 0:
            exec(f'mouse.press("{self.button}")')
            time.sleep(self.duration_s)
            exec(f'mouse.release("{self.button}")')
        else:
            exec(f'mouse.click("{self.button}")')


class WackyWasd(Action):
    kind = 'wackywasd'
    duration_s: float = 0.0

    def validate(self):
        self.duration_s = float(self._args[0])

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
            if i == 3 and len(diff) < 1:
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
            time.sleep(self.duration_s)
            keyboard.unhook_all()
        threading.Thread(target=reset).start()


for clz in Action.__subclasses__():
    _registry[clz.kind] = clz
