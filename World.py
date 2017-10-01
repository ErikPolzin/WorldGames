from Civilisations import Node, Empire, merge_tuples
from Biomes import *
from PIL import Image, ImageTk
import random
import itertools
import noise


class World(object):

    background = "#333333"
    biomes = [Plain, Forest, Desert, Ocean, Default]
    resources = []
    base_noise = random.random()

    GRADIENT = 5
    SIZE = 200
    SIZE_COEFF = 3/SIZE
    SLOPE = 40
    BUFFER = 10

    def __init__(self):
        self.all_nodes = {}
        self.empires = {}
        self.size = (self.SIZE, self.SIZE)

    # generate a random height map
    def map(self, length):
        names = ["Rome", "Greece", "Macedonia", "Huns", "Mongols", "Japanese", "Britons", "Celts"]
        self.civs = names[:min(len(names), length)]
        self.colours = []

        for i in self.civs:
            col = (random.randrange(255), random.randrange(255), random.randrange(255))
            self.colours.append(col)

        coords = itertools.product(range(self.SIZE), repeat=2)   # create all coordinate pairs

        # map perlin noise landscapes
        for coord in coords:
            height = noise.snoise3(coord[0]*self.SIZE_COEFF, coord[1]*self.SIZE_COEFF, self.base_noise) * self.SLOPE
            self.all_nodes[coord] = Node(coord, height, None)   # create the node
            seed = height/20

            for _class in self.biomes:
                # create a seperate noise map (linked to the height), determining if a biome is part of a node
                # lower cutoff means more likelihood for that biome
                val = noise.snoise3(coord[0]*_class.size, coord[1]*_class.size, seed)
                if val > _class.cutoff:
                    val = (val-_class.cutoff)/(1-_class.cutoff) # normalise between 0 and 1
                    biome = _class(val)
                    self.all_nodes[coord].biomes.append(biome)

    def setup(self):
        for i in range(len(self.civs)):
            name = self.civs[i]
            colour = self.colours[i]
            while True:
                loc = (random.randrange(self.BUFFER, self.SIZE-self.BUFFER),
                        random.randrange(self.BUFFER, self.SIZE-self.BUFFER))
                if self.all_nodes[loc].empire == None:
                    break
            empire = Empire(name, colour, loc, self.all_nodes)
            self.empires[name] = {"colour":colour, "class":empire}

    # generate empire bounds
    def generate(self, incr):
        for i in range(incr):
            for empire in self.empires:
                self.empires[empire]["class"].grow()
            progress = round((i/incr) * 100)
            print("Generating Empires: {}%".format(progress), end="\r")

    def fill(self, node, **kwargs): # this is bilinear interpolation, in case you wanted to know
        startx, starty = node.loc
        colours = [self.all_nodes[(startx, starty)].colour(**kwargs),
                self.all_nodes[(startx+1, starty)].colour(**kwargs),
                self.all_nodes[(startx, starty+1)].colour(**kwargs),
                self.all_nodes[(startx+1, starty+1)].colour(**kwargs)]

        for x in range(self.GRADIENT):
            x_weight = x/self.GRADIENT
            x_weights = [x_weight, 1-x_weight]
            x_col1 = merge_tuples(colours[0], colours[1], weights=x_weights)
            x_col2 = merge_tuples(colours[2], colours[3], weights=x_weights)

            for y in range(self.GRADIENT):
                y_weight = y/self.GRADIENT
                y_weights = [y_weight, 1-y_weight]

                # using a generator for speed
                yield merge_tuples(x_col1, x_col2, weights=y_weights)

    # show the image
    def show(self, **kwargs):
        pixel_size = (self.SIZE * self.GRADIENT, self.SIZE * self.GRADIENT)
        image = Image.new("RGB", pixel_size, color=self.background)
        pixels = image.load()
        i = 0

        # loop through node coordinates
        for y in range(self.SIZE - 1):
            for x in range(self.SIZE - 1):
                node = self.all_nodes[(x, y)]

                # convert to pixel coordinates
                pixel_x = x * self.GRADIENT
                pixel_y = y * self.GRADIENT
                n = 0

                # colour the pixels according to the interpolation
                for col in self.fill(node, **kwargs):
                    x1 = pixel_x + (n // self.GRADIENT)
                    y1 = pixel_y + (n % self.GRADIENT)
                    pixels[x1, y1] = col
                    n += 1
            progress = round((i/self.SIZE)*100)
            print("Generating Map: {}%".format(progress), end="\r")
            i += 1
        image.show()


gusath = World()
gusath.map(7)
gusath.setup()
gusath.generate(200)
gusath.show(height=False)
