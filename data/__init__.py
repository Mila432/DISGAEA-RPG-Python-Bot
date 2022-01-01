import json

data = {
    'equip': [],
    'characters': [],
    'stages': [],
    'items': [],
    'units': [],
    'weapon': [],
}

with open('data/characters.json') as f:
    data['characters'] = json.load(f)
with open('data/equipment.json') as f:
    data['equip'] = json.load(f)
with open('data/items.json') as f:
    data['items'] = json.load(f)
with open('data/stages.json') as f:
    data['stages'] = json.load(f)
with open('data/units.json') as f:
    data['units'] = json.load(f)
with open('data/weapons.json') as f:
    data['weapon'] = json.load(f)
