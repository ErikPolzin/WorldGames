import random
import itertools
import copy
import math

def chance(val):
    assert(0 <= val <= 1)
    choice = random.random()
    if choice <= val:
        return True
    return False

# take the average of x rgb tuples. Has the effect of an overlay
def merge_tuples(*args):
    result = []
    # if the tuples are different lengths, take the shortest one
    length = min([len(i) for i in args])
    for i in range(length):
        # take the average
        val = sum([tup[i] for tup in args])/len(args)
        result.append(round(val))
    result = tuple(result)
    return result

class Node(object):
    # one step away from the node in each direction
    steps = list(itertools.permutations((1, -1, 0), 2))

    def __init__(self, loc, height, empire):
        self.loc = loc
        self.height = height
        self.empire = empire
        self.biomes = []
        self.resources = []
        self.colour = (0, 0, 0)

    def neighbours(self, randomise=True):
        nodes = [(self.loc[0]+step[0], self.loc[1]+step[1]) for step in self.steps]
        if randomise:
            random.shuffle(nodes)
        return nodes

    def merge_biomes(self, _filter=None):
        self.colour = (0, 0, 0, 0)
        if self.biomes == []:
            return self.colour
        if _filter:
            top_idx = _filter
        else:
            top_idx = min([b.order for b in self.biomes])
        top_layers = [i for i in self.biomes if i.order == top_idx]
        self.biomes = top_layers

        for layer in top_layers:
            add_colour = layer.shade
            self.colour = merge_tuples(self.colour, add_colour)
        return self.colour

    def prob(self):
        probability = 0
        for biome in self.biomes:
            test_prob = (biome.prob * biome.intensity)/len(self.biomes)
            if test_prob < 0:
                test_prob = (biome.prob-(biome.intensity*biome.prob))/len(self.biomes)
            probability += test_prob
        return max(0, probability)


class Empire(object):
    slope_tolerance = 1/20    # difficulty of advancing up a slop
    def __init__(self, name, colour, loc, node_list):
        self.name = name
        self.colour = colour
        self.location = loc
        self.node_list = node_list

        capitol_loc = node_list[loc]
        self.nodes = [capitol_loc,]
        self.border_nodes = [capitol_loc,]

    # passive expansion
    def grow(self):

        random.shuffle(self.border_nodes)

        for b_node in self.border_nodes:
            coords = b_node.loc

            # absolute coords, in random order
            neighbours = b_node.neighbours()

            # look for a neighbouring node with no empire assigned yet
            for n in neighbours:
                # if the coordinates are outside the bounds of the node list move to next neighbour
                try:
                    test_node = self.node_list[n]
                except KeyError:
                    continue

                # check that the node doesn't belong to anyone else
                if test_node.empire == None:
                    # randomness factors
                    dz = (test_node.height - b_node.height)*(1/self.slope_tolerance)
                    if dz > 0:
                        angle = 1-(math.atan(dz)/(math.pi/2))
                        if not chance(angle):
                            continue

                    if not chance(test_node.prob()):
                        continue

                    self.node_list[n].empire = self # register the node
                    self.nodes.append(test_node)    # claim the node
                    self.border_nodes.append(test_node)

                    # if there are no free nodes next to the selected node, remove it from the border
                    self.clarify_borders()
                    return True
        # if, after looping through all the border nodes, a free node has been found, the empire cannot grow
        # it must CONQUER!
        return False

    def clarify_borders(self):
        for node in self.border_nodes:
            try:
                if len([i for i in node.neighbours() if self.node_list[i].empire != self]) == 0:
                    self.border_nodes.remove(node)
            except KeyError:
                pass

    def __str__(self):
        return self.name
