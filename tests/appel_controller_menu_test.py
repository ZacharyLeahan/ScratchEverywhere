#!/usr/bin/env python3
"""Validate Appel preparation against a caller-supplied original archive."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_appel', root / 'scripts/prepare-appel.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = Path(sys.argv[1])
with zipfile.ZipFile(source) as archive:
    original = json.loads(archive.read('project.json'))
prepared = module.prepare(copy.deepcopy(original))
for old, new in zip(original['targets'], prepared['targets']):
    assert old['costumes'] == new['costumes'] and old['sounds'] == new['sounds']
    if old['name'] != 'menu' and not old['isStage']:
        assert old == new, old['name'] + ' gameplay changed'
menu = next(t for t in prepared['targets'] if t['name'] == 'menu')
blocks = menu['blocks']
hats = [b for k, b in blocks.items() if k.startswith('xbox-menu-') and b['opcode'] == 'event_whenkeypressed']
assert sorted(b['fields']['KEY_OPTION'][0] for b in hats) == ['b', 'down arrow', 'l', 'left arrow', 'right arrow', 'space', 'up arrow']
space = next(b for b in hats if b['fields']['KEY_OPTION'][0] == 'space')
guard = blocks[space['next']]
assert guard['opcode'] == 'control_if'
mode = blocks[guard['inputs']['SUBSTACK'][1]]
assert mode['opcode'] == 'data_setvariableto'
wait = blocks[mode['next']]
assert wait['opcode'] == 'control_wait_until', 'Must release A before transitioning'

def evaluate(value, state, identity, focus, mode=1, mouse=False):
    if isinstance(value, list):
        if value[0] == 3 and isinstance(value[1], list) and value[1][0] == 12:
            return {'GAME STATE': state, 'id': identity, 'Xbox menu selection': focus, 'Xbox controller menus': mode}[value[1][1]]
        if isinstance(value[1], list): return value[1][1]
        return evaluate(value[1], state, identity, focus, mode, mouse)
    b = blocks[value]
    if b['opcode'] == 'sensing_touchingobject': return mouse
    args = [evaluate(v, state, identity, focus, mode, mouse) for v in b['inputs'].values()]
    return {'operator_equals': lambda: str(args[0]) == str(args[1]),
            'operator_contains': lambda: str(args[1]) in str(args[0]),
            'operator_and': lambda: all(args), 'operator_or': lambda: any(args), 'operator_not': lambda: not args[0]}[b['opcode']]()
allowed = guard['inputs']['CONDITION']
for state, identity, focus, expected in [
    ('MENU', 'PLAY', 1, True), ('MENU', 'EDITOR', 1, False),
    ('MENU', 'EDITOR', 2, True), ('MENU', 'AUDIO ON', 3, True),
    ('MENU LEVELS', 'SELECT', 1, True), ('MENU LEVELS', 'PLAY', 1, False),
    ('PLAY', 'PLAY', 1, False), ('PLAY', 'SELECT', 1, False),
    ('MENU OFF', 'SELECT', 1, False), ('MENU', '', 1, False),
]:
    assert evaluate(allowed, state, identity, focus) == expected, (state, identity, focus)
hover = blocks['Y9iOLfz]Q%ofF`ur6i7n']['inputs']['CONDITION']
assert not evaluate(hover, 'MENU', 'PLAY', 2, mode=1, mouse=True), 'Old pointer hover must not create a second focus'
assert evaluate(hover, 'MENU', 'EDITOR', 2, mode=1, mouse=False)
assert evaluate(hover, 'MENU', 'EDITOR', 1, mode=0, mouse=True), 'Pointer mode must preserve authored hover'
assert evaluate(hover, 'PLAY', 'EDITOR', 1, mode=1, mouse=True), 'Other authored menus retain pointer hover'
try: module.prepare(prepared)
except ValueError: pass
else: raise AssertionError('Preparation must refuse repeated application')
print('PASS: assets/gameplay preserved; menu keys, focus guards, release gate, duplicate refusal')
