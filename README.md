# Katheryne

Katheryne is watching silently from the Adventurer's Guild, always.

## Running

You'll need: `python3.9`

```
$ python3 -m venv --prompt katheryne venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ echo '<YOUR DISCORD BOT TOKEN>' > .discord_token
$ python -m katheryne
```


### Windows peeps

The overall flow is the same, but the naming is a bit different. If the above doesn't work, try:

```
$ py -3.9 -m venv --prompt katheryne venv
$ . venv/Scripts/activate
$ py -3.9 -m pip install -r requirements.txt
$ echo '<YOUR DISCORD BOT TOKEN>' > .discord_token
$ py -3.9 -m katheryne
```