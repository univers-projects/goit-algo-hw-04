import math
from typing import List, Tuple
import matplotlib.pyplot as plt

Point = Tuple[float, float]


def koch_segment(p1: Point, p2: Point, level: int) -> List[Point]:
    """Return list of points from p1 to p2 (inclusive) for a Koch curve of given level."""
    if level == 0:
        return [p1, p2]

    (x1, y1), (x2, y2) = p1, p2
    dx, dy = (x2 - x1) / 3.0, (y2 - y1) / 3.0

    a = (x1 + dx, y1 + dy)
    c = (x1 + 2 * dx, y1 + 2 * dy)

    cos60, sin60 = 0.5, math.sqrt(3) / 2.0
    rx, ry = dx * cos60 - dy * sin60, dx * sin60 + dy * cos60
    b = (a[0] + rx, a[1] + ry)

    s1 = koch_segment(p1, a, level - 1)
    s2 = koch_segment(a, b, level - 1)
    s3 = koch_segment(b, c, level - 1)
    s4 = koch_segment(c, p2, level - 1)

    return s1[:-1] + s2[:-1] + s3[:-1] + s4


def build_snowflake(level: int, scale: float = 1.0) -> List[Point]:
    """Build the full list of points for the Koch snowflake boundary."""
    h = math.sqrt(3) / 2.0
    p1 = (-0.5 * scale, -h / 3 * scale)
    p2 = (0.5 * scale, -h / 3 * scale)
    p3 = (0.0, 2 * h / 3 * scale)

    edge1 = koch_segment(p1, p2, level)[:-1]
    edge2 = koch_segment(p2, p3, level)[:-1]
    edge3 = koch_segment(p3, p1, level)
    return edge1 + edge2 + edge3


if __name__ == "__main__":
    try:
        level = int(input("Enter recursion level (>=0): "))
    except ValueError:
        print("Invalid input. Using level 0.")
        level = 0

    pts = build_snowflake(level=level, scale=1.0)
    xs, ys = zip(*pts)

    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, linewidth=1)
    plt.axis("equal")
    plt.axis("off")
    plt.title(f"Koch Snowflake (level={level})")
    plt.show()
