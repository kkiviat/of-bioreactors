def kInlet(u, I):
    return 1.5 * (u * I) ** 2


def epsilonPrandtl(k, l):
    """
    Estimates inlet epsilon value for given k and
    Prandtl mixing length l (~ 0.07 L for characteristic
    length L for a pipe)
    """
    return 0.09**0.75 * k**1.5 / l


def epsilonViscosityRatio(k, viscosity_ratio, mu, rho):
    """
    Estimates inlet epsilon value for given k and ratio of
    turublent viscosity to molecular viscosity (typically ~ 1 - 100)
    """
    return 0.09 * rho * k**2 / (viscosity_ratio * mu)
