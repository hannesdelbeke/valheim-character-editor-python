### Summary

This is a shameless lift and shift of byt3m's Valheim Character Editor that I reimplemented in python

- https://github.com/byt3m/Valheim-Character-Editor

### Usage

This is meant to be used from a REPL prompt or imported into a script, no interface is provided. Instantiate a
new `Character` with your input files location, edit any desired fields, and use the `dump` method to save it to a new
output file.

1. **THERE IS NO VALIDATION PROVIDED** - don't set a field that should be a `float` to an `integer`, don't pass
   a `string` when `bytes` are expected, etc.
2. **THERE IS NO BACKUP FUNCTIONALITY PROVIDED** - make sure you are not overwriting your input file, always dump to an
   intermediate file and save a copy of the pre-changes file.

### Example

```python
from valheim import Character
from pathlib import Path

save_path = Path("/home/me/.config/unity3d/IronGate/Valheim/characters")  # different on windows
character = Character(save_path / "me.fch")

for skill in character.skills:
    skill.level = 99.9  # don't set this float field to an integer

for item in character.inventory:
    if item.name == b'Bronze':
        item.stack = 30  # don't set this to an invalid quantity

character.name = b'superme'  # don't set this bytes field to a string

# DON'T overwrite your original character
with open(save_path / "superme.fch", "wb") as f:
    character.dump(f)
```

