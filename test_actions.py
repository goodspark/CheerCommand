import actions
from actions import Action


def test_loads_registry():
    assert 'keypress' in actions._registry
    assert 'click' in actions._registry
    assert 'wait' in actions._registry
    assert 'wackywasd' in actions._registry


def test_keypress_with_duration():
    a = Action.from_config({
        'kind': 'keypress',
        'args': ['a', 100],
    })
    assert isinstance(a, actions.KeyPress)
    assert a.key == 'a'
    assert a.duration_s == 100.0


def test_keypress():
    a = Action.from_config({
        'kind': 'keypress',
        'args': ['a'],
    })
    assert isinstance(a, actions.KeyPress)
    assert a.key == 'a'
    assert a.duration_s == 0.0


def test_wait():
    a = Action.from_config({
        'kind': 'wait',
        'args': [10.0],
    })
    assert isinstance(a, actions.Wait)
    assert a.duration_s == 10.0


def test_click_with_duration():
    a = Action.from_config({
        'kind': 'click',
        'args': ['left', 0.45],
    })
    assert isinstance(a, actions.Click)
    assert a.button == 'left'
    assert a.duration_s == 0.45


def test_click():
    a = Action.from_config({
        'kind': 'click',
        'args': ['left'],
    })
    assert isinstance(a, actions.Click)
    assert a.button == 'left'
    assert a.duration_s == 0.0
