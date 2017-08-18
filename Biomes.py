class Biome:
    def __init__(self, n, col):
        self.intensity = n
        self.shade = tuple([round(n*c) for c in list(col)])

class Default(Biome):
    colour = (118, 77, 25)
    order = 1
    prob = .0005
    size = .003
    cutoff = -1

    def __init__(self, n):
        Biome.__init__(self, n, self.colour)

    def place(self, node):
        pass

class Desert(Biome):
    colour = (188, 170, 66)
    cutoff = .3
    size = .03
    order = 1
    prob = -.2

    def __init__(self, n):
        Biome.__init__(self, n, self.colour)

    def place(self, node):
        pass

class Ocean(Biome):
    colour = (76, 103, 182)
    cutoff = .35
    size = .015
    order = 0
    prob = 0

    def __init__(self, n):
        Biome.__init__(self, n, self.colour)

    def place(self, node):
        pass

class Plain(Biome):
    colour = (132, 188, 52)
    cutoff = .01
    size = .005
    order = 1
    prob = +.7

    def __init__(self, n):
        Biome.__init__(self, n, self.colour)

    def place(self, node):
        pass

class Forest(Biome):
    colour = (47, 122, 47)
    cutoff = .30
    size = .02
    order = 1
    prob = +.5

    def __init__(self, n):
        Biome.__init__(self, n, self.colour)

    def place(self, node):
        pass
