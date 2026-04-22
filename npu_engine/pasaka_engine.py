import csv, random, os
from pathlib import Path

_HERE = Path(__file__).parent.parent
_CSV = _HERE / 'datasets' / 'iching' / 'pasaka.csv'

def _load():
    rows = {}
    with open(_CSV) as f:
        for r in csv.DictReader(f):
            key = (int(r['dice_1']), int(r['dice_2']), int(r['dice_3']))
            rows[key] = r
    return rows

_DATA = _load()

def cast(field_state=None):
    dice = (random.randint(1,4), random.randint(1,4), random.randint(1,4))
    row = _DATA[dice]
    result = dict(row)
    result['dice'] = list(dice)
    if field_state:
        result['field_score'] = _score(row, field_state)
    return result

def _score(row, fs):
    score = {'excellent':1.0,'very_good':0.8,'good':0.6,'mixed':0.4}.get(row['quality'], 0.5)
    return round(score, 3)

def get(dice_1, dice_2, dice_3):
    return dict(_DATA.get((int(dice_1),int(dice_2),int(dice_3)), {}))
