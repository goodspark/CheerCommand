# CheerCommand
http://twitch.tv/johnlonnie

IRCV3 Chat Bot that listens for cheers and allows chat to control mouse and keyboard

Utilizes Mouse Lib
https://pypi.org/project/mouse/

Utilizes Keyboard Lib
https://pypi.org/project/keyboard/

Utility.py
Process tags from IRCv3

## Cheer command configuration

Cheer commands are composed of sequences of actions. An action is a low-level 'thing'
and can be anything, from injecting key presses to running any other code. Actions must
map to code defined in `actions.py`, identified by the `kind` field in the configs.

The cheer command config is set by the `currentGameConfig` filename in the `cfg.py` file.

The expected format is:

```yaml
commands:
  - name: name of command
    message: message sent to chat when command is run
    cost: 100 # normal bits cost
    discount: 50 # discount bits cost, for subscribers
    actions:
      - kind: keypress # this must map to actual actions defined in actions.py
        args: [a] # oneliner form of list is used here for brevity.
        # args that get passed to the action when it's run.
  - name: etc...
```
