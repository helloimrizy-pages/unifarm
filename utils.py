import math

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def lerp_color(color1, color2, t):
    """Linear interpolation between two colors"""
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    if len(color1) > 3 and len(color2) > 3:
        a = int(color1[3] + (color2[3] - color1[3]) * t)
        return (r, g, b, a)
    return (r, g, b)