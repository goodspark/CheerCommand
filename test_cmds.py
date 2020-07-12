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


def test_run_name(normal_config):
    cmds.from_config(normal_config)
    cmd = cmds.run('asd')
    assert cmd is not None


@pytest.mark.parametrize('cost,discount,name', [
    (100, False, 'asd'),
    (50, True, 'asd'),
    (200, False, 'zxc'),
    (200, True, None),
    (100, True, 'zxc'),
    (123123123, False, None),
    (123123123, True, None),
])
def test_run_index(normal_config, cost, discount, name):
    cmds.from_config(normal_config)
    cmd = cmds.run(cost, discount=discount)
    if name is None:
        assert cmd is None
    else:
        assert cmd.name == name


@pytest.mark.parametrize('i,name', [
    (0, 'asd'),
    (-1, None),
    (1, 'zxc'),
    (40, None),
])
def test_get_nth(i, name):
    cmd = cmds.get_nth(i)
    if name is None:
        assert cmd is None
    else:
        assert cmd.name == name


def test_run_random():
    cmd = cmds.run_random()
    assert cmd.name in {'asd', 'zxc'}
