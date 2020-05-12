import math


def get_distance(p1, p2):
    # функция нахождения дистанции по координатам
    radius = 6373.0

    lon1 = math.radians(float(p1[0]))
    lat1 = math.radians(float(p1[1]))
    lon2 = math.radians(float(p2[0]))
    lat2 = math.radians(float(p2[1]))

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    distance = radius * c
    return distance
