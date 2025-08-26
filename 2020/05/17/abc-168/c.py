from math import cos, radians


def law_of_cosines(a, b, theta):
    """
    Calculate the length of the third side of a triangle using the law of cosines.

    :param a: Length of side a
    :param b: Length of side b
    :param theta: Angle in degrees between sides a and b
    :return: Length of side c
    """
    return (a**2 + b**2 - 2 * a * b * cos(radians(theta))) ** 0.5


def clock_angle(h, m):
    """
    Calculate the angle between the hour and minute hands of a clock.
    :param h: Hour (0-12)
    :param m: Minute (0-59)
    :return: Angle in degrees
    """
    h_angle = (h*60 + m) / 720 * 360
    m_angle = m / 60 * 360
    return abs(h_angle - m_angle) % 360


A, B, H, M = map(int, input().split())

theta = clock_angle(H, M)  # Example usage, should return 15.0

ans = law_of_cosines(A, B, theta)
print(ans)  # Output the length of the third side
