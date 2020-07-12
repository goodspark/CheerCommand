import yaml

import cmds

#game
currentGameConfig = "pubg.yml"

#channel point identifiers - when a user redeems channel points, the channel point will have an identifier (e.g. "b3df3074-eb94-4f44-811a-1815835edfdd")
channelPoint1 = ""

with open(currentGameConfig) as f:
    config = yaml.safe_load(f)
    cmds.from_config(config)
