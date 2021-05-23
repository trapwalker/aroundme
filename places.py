
from math import sqrt
from pathlib import Path
import json


def dist_coord(a, b):
    c = sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    return c / 180.0 * 3.14 * 6371000


def dist_points(a: dict, b: dict):
    return dist_coord(a['geometry']['coordinates'], b['geometry']['coordinates'])


def import_points(filename=Path('points.geojson')):
    with filename.open('r', encoding='utf-8') as fp:
        return json.load(fp)['features']


def to_tags(s) -> set:
    if not s:
        return set()
    if isinstance(s, str):
        return set(filter(None, map(str.strip, s.split(','))))
    if isinstance(s, set):
        return s
    return set(s)


def fltr(points, tags, neg=False):
    tags = to_tags(tags)
    return [p for p in points if neg != tags.issubset(to_tags(p['properties']['tags']))]


POINTS = import_points()
ME = fltr(POINTS, tags='ME')[0]
POINTS = fltr(POINTS, tags='ME', neg=True)


def sort_relative(points: list, center: dict = ME):
    points.sort(key=lambda p: dist_points(p, center))


sort_relative(POINTS)
