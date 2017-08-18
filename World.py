from Civilisations import Node, Empire, merge_tuples
from Biomes import *
from PIL import Image, ImageTk
import random
import itertools
import noise


class World(object):

    background = "#333333"
    buffer = 10
    slope = 40
    biomes = [Plain, Forest, Desert, Ocean, Default]
    resources = []
    base_noise = random.random()

    def __init__(self, size):
        self.all_nodes = {}
        self.empires = {}
        self.size = (size, size)
        self.rel_size = 3/size

    def setup_test_env(self, length):
        #self.civs = ["Rome", "Greece", "Macedonia", "Huns", "Mongols", "Japanese", "Britons", "Celts"]
        self.civs = [str(i) for i in range(length)]
        self.colours = []
        for i in self.civs:
            col = (random.randrange(255), random.randrange(255), random.randrange(255))
            self.colours.append(col)

        assert (len(self.civs) == len(self.colours))

        coords = itertools.product(range(self.size[0]), repeat=2)   # create all coordinate pairs

        # map perlin noise landscapes
        for coord in coords:
            height = noise.snoise3(coord[0]*self.rel_size, coord[1]*self.rel_size, self.base_noise) * self.slope
            self.all_nodes[coord] = Node(coord, height, None)   # create the node
            seed = height/20

            for _class in self.biomes:
                val = noise.snoise3(coord[0]*_class.size, coord[1]*_class.size, seed)
                if val > _class.cutoff:
                    val = (val-_class.cutoff)/(1-_class.cutoff)
                    biome = _class(val)
                    self.all_nodes[coord].biomes.append(biome)
            self.all_nodes[coord].merge_biomes(_filter=None)

    def start(self):
        for i in range(len(self.civs)):
            name = self.civs[i]
            colour = self.colours[i]
            while True:
                loc = (random.randrange(self.buffer, self.size[0]-self.buffer),
                        random.randrange(self.buffer, self.size[1]-self.buffer))
                if self.all_nodes[loc].empire == None:
                    break
            empire = Empire(name, colour, loc, self.all_nodes)
            self.empires[name] = {"colour":colour, "class":empire}

    def setup(self, incr):
        for i in range(incr):
            for empire in self.empires:
                self.empires[empire]["class"].grow()
            progress = round((i/incr) * 100)
            print("{}% completed".format(progress), end="\r")

    def show(self, biome=False, height=True):
        emp_image = Image.new("RGB", tuple(self.size), color=self.background)
        height_image = Image.new("L", tuple(self.size), color=self.background)
        emp_pixels = emp_image.load()
        height_pixels = height_image.load()

        for i in self.all_nodes:
            node = self.all_nodes[i]
            if height:
                height_shade = int((((node.height/self.slope)+1)/2)*255)
                height_pixels[node.loc] = height_shade
            if biome:
                biome_col = node.colour
                emp_pixels[node.loc] = biome_col
        for i in self.empires:
            empire = self.empires[i]["class"]
            col = self.empires[i]["colour"]
            for node in empire.nodes:
                loc = node.loc
                emp_pixels[loc] = merge_tuples(col, emp_pixels[loc])
        emp_image.show()
        if height:
            height_image.show()


gusath = World(150)
gusath.setup_test_env(7)
gusath.start()
gusath.setup(2500)
gusath.show(biome=True, height=False)
