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
def merge_tuples(*args, weights=None, default=0):
    if not weights:
        weights = [1 for i in range(len(args))]

    result = []
    max_len = max([len(i) for i in args])
    weight_len = sum([i for i in weights])

    for tup_idx in range(max_len):
        summed = 0
        for rgb_idx in range(len(args)):
            try:
                value = args[rgb_idx][tup_idx]
            except IndexError:
                value = default
            weight = weights[rgb_idx]
            #print(value, weight)
            average = value * weight / weight_len
            summed += average
        result.append(round(summed))
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

    def neighbours(self, randomise=True):
        nodes = [(self.loc[0]+step[0], self.loc[1]+step[1]) for step in self.steps]
        if randomise:
            random.shuffle(nodes)
        return nodes

    def prob(self):
        probability = 0
        for biome in self.biomes:
            test_prob = (biome.prob * biome.intensity)/len(self.biomes)
            if test_prob < 0:
                test_prob = (biome.prob-(biome.intensity*biome.prob))/len(self.biomes)
            probability += test_prob
        return max(0, probability)

    def colour(self, height=True, empire=True, _filter=None):
        colours = []
        weights = []

        if self.biomes == []:
            return (0, 0, 0, 0)
        if _filter:
            top_idx = _filter
        else:
            top_idx = min([b.order for b in self.biomes])
        top_layers = [i for i in self.biomes if i.order == top_idx]

        if height:
            colours.append((0, 0, 0))
            weights.append(self.height/40)

        if empire and self.empire:
            colours.append(self.empire.colour)
            weights.append(self.empire.opacity)

        for layer in top_layers:
            colours.append(layer.colour)
            weights.append(layer.intensity)

        return merge_tuples(*colours, weights=weights)


class Empire(object):

    slope_tolerance = 1/20    # difficulty of advancing up a slope
    opacity = .8

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
