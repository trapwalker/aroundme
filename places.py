
from math import sqrt


def distance(a, b):
    c = sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    return c / 180.0 * 3.14 * 6371000


