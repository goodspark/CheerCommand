from typing import List

import attr
import pytest
import yaml

import actions
import cmds


@pytest.fixture
def normal_config():
    return yaml.safe_load("""
    commands:
      - name: asd
        message: asdasdasd
        cost: 100
        discount: 50
        actions:
          - kind: wait
            args: [0.05]
      - name: zxc
        message: zxczxczxc
        cost: 200
        discount: 100
        actions:
          - kind: wait
            args: [0.01]
          - kind: wait
            args: [0.02]
    """)


@pytest.fixture
def chat():
    """ A mock for the chat function so it can be tested. Saves sent messages. """
    @attr.s(auto_attribs=True, frozen=True, slots=True)
    class Chatter:
        msgs: List[str] = attr.ib(factory=list)

        def __call__(self, *args, **kwargs):
            self.msgs.append(args[0])

    return Chatter()


def test_from_config(normal_config):
    commands = cmds.from_config(normal_config)
    cmd = commands['asd']
    assert cmd.message == 'asdasdasd'
    assert cmd.cost == 100
    assert cmd.discount == 50
    assert len(cmd._actions) == 1
    assert isinstance(cmd._actions[0], actions.Wait)
    assert cmd._actions[0].duration_s == 0.05
    cmd = commands['zxc']
    assert cmd.message == 'zxczxczxc'
    assert cmd.cost == 200
    assert cmd.discount == 100
    assert len(cmd._actions) == 2
    assert isinstance(cmd._actions[0], actions.Wait)
    assert cmd._actions[0].duration_s == 0.01
    assert isinstance(cmd._actions[1], actions.Wait)
    assert cmd._actions[1].duration_s == 0.02


def test_checks_collisions(normal_config):
    cmd2 = normal_config['commands'][1]
    # Same name should cause an error
    cmd2['name'] = 'asd'
    with pytest.raises(ValueError):
        cmds.from_config(normal_config)
    cmd2['name'] = 'zxc'

    # Same cost should cause an error
    cmd2['cost'] = 100
    with pytest.raises(ValueError):
        cmds.from_config(normal_config)
    cmd2['cost'] = 200

    # Same discount should cause an error
    cmd2['discount'] = 50
    with pytest.raises(ValueError):
        cmds.from_config(normal_config)


def test_run_name(normal_config, chat):
    cmds.from_config(normal_config)
    cmd = cmds.run('asd', chat)
    assert cmd is not None
    assert chat.msgs == ['asdasdasd']


def test_run_name_no_match(normal_config, chat):
    cmds.from_config(normal_config)
    cmd = cmds.run('zxczxczxczxczxc', chat)
    assert cmd is None
    assert chat.msgs == []


@pytest.mark.parametrize('cost,discount,name', [
    (100, False, 'asd'),
    (50, True, 'asd'),
    (200, False, 'zxc'),
    (200, True, None),
    (100, True, 'zxc'),
    (123123123, False, None),
    (123123123, True, None),
])
def test_run_index(normal_config, cost, discount, name, chat):
    cmds.from_config(normal_config)
    cmd = cmds.run(cost, chat, discount=discount)
    if name is None:
        assert cmd is None
        assert chat.msgs == []
    else:
        assert cmd.name == name
        assert chat.msgs == [cmd.message]


@pytest.mark.parametrize('i,name', [
    (0, 'asd'),
    (-1, None),
    (1, 'zxc'),
    (40, None),
])
def test_run_nth(i, name, chat):
    cmd = cmds.run_nth(i, chat)
    if name is None:
        assert cmd is None
        assert chat.msgs == []
    else:
        assert cmd.name == name
        assert chat.msgs == [cmd.message]


def test_run_random(chat):
    cmd = cmds.run_random(chat)
    assert cmd.name in {'asd', 'zxc'}
    assert len(chat.msgs) == 1
