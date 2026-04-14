import math

def offset_line(x1, y1, x2, y2, offset):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)

    if length == 0:
        return x1, y1, x2, y2

    ux = dx / length
    uy = dy / length

    # perpendicular vector
    px = -uy
    py = ux

    return (
        x1 + px * offset,
        y1 + py * offset,
        x2 + px * offset,
        y2 + py * offset
    )