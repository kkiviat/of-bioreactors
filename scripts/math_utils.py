def closeTo(x1, x2, epsilon=1e-6):
    if not x1 or not x2:
        return False
    return abs(x1 - x2) < epsilon


def closeToAny(x1, x2_list, epsilon=1e-6):
    for x2 in x2_list:
        if closeTo(x1, x2, epsilon):
            return True
    return False
