# Fall 2012 6.034 Lab 2: Search
#
# Your answers for the true and false questions will be in the following form.
# Your answers will look like one of the two below:
#ANSWER1 = True
#ANSWER1 = False

# 1: True or false - Hill Climbing search is guaranteed to find a solution
#    if there is a solution
ANSWER1 = None

# 2: True or false - Best-first search will give an optimal search result
#    (shortest path length).
#    (If you don't know what we mean by best-first search, refer to
#     http://courses.csail.mit.edu/6.034f/ai3/ch4.pdf (page 13 of the pdf).)
ANSWER2 = None

# 3: True or false - Best-first search and hill climbing make use of
#    heuristic values of nodes.
ANSWER3 = None

# 4: True or false - A* uses an extended-nodes set.
ANSWER4 = None

# 5: True or false - Breadth first search is guaranteed to return a path
#    with the shortest number of nodes.
ANSWER5 = None

# 6: True or false - The regular branch and bound uses heuristic values
#    to speed up the search for an optimal path.
ANSWER6 = None

# Import the Graph data structure from 'search.py'
# Refer to search.py for documentation
from search import Graph
import copy

## Optional Warm-up: BFS and DFS
# If you implement these, the offline tester will test them.
# If you don't, it won't.
# The online tester will not test them.

class data_node(object):
    def __init__(self, list_object, left_point=None, right_point=None):
        self.data = list_object
        self.left_point = left_point
        self.right_point = right_point

    def set_right_node(self, node_to_set):
        self.right_point = node_to_set

    def set_left_node(self, node_to_set):
        self.left_point = node_to_set

class data_queue(object):
    def __init__(self):
        self.beginning = None
        self.ending = None

    def add_data_node(self, node_to_add):
        if (self.ending is None) and (self.beginning is None):
            # completely empty queue
            self.beginning = node_to_add
            self.ending = node_to_add
        else:
            self.ending.set_right_node(node_to_add)
            node_to_add.set_left_node(self.ending)
            self.ending = node_to_add

    def get_next(self):
        if self.beginning is None:
            return_node = None
            print "ERROR: QUEUE IS EMPTY, CANNOT RETRIEVE DATA"
        else:
            return_node = self.beginning
            self.beginning = self.beginning.right_point
            if not self.beginning is None:
                self.beginning.set_left_node(None)
            if self.beginning is None:
                print "QUEUE IS EMPTY"
            return_node.set_right_node(None)

        return return_node

class path_list(object):
    def __init__(self, graph, path):
        self.graph = graph
        self.path = path
        if isinstance(path, list):
            size = len(path)
        else:
            raise IOError("ERROR: MUST INITIALIZE WITH A PATH LIST")

    def add_next_node(self, node):
        last = self.path[len(self.path)-1]
        if self.graph.are_connected(last, node):
            self.path.append(node)
        else:
            raise IOError("Given path is invalid, some nodes not connected")

    @property
    def length(self):
        if self.size > 1:
            length = 0
            for i in range(self.size-1):
                start = self.path[i]
                end = self.path[i+1]
                if self.graph.are_connected(start, end):
                    length += self.graph.get_edge(start, end).length
                else:
                    raise IOError("Given path is invalid, some nodes not connected")
            return length
        else:
            return 0
    @property
    def size(self):
        return len(self.path)

    @property
    def last_idx(self):
        return len(self.path) - 1



def bfs(graph, start, goal):
    queue = data_queue()
    best_path = None
    # initialize the queue
    first_connections = graph.get_connected_nodes(start)
    if len(first_connections) == 0:
        # the start node is completely empty
        go = False
    else:
        go = True
        count = 0
        for connections in first_connections:
            count += 1
            path = path_list(graph, [start, connections])
            this = data_node(path)
            queue.add_data_node(this)
    print count
    next_up = queue.get_next()
    if next_up is None:
        go = False
    # begin iterating
    while go:
        old_path_object = next_up.data #path_list object
        old_path = old_path_object.path #list of nodes forthe path
        next_connections = graph.get_connected_nodes(old_path[old_path_object.last_idx])
        for connection in next_connections:
            if connection == goal:
                old_path_object.add_next_node(connection)
                if best_path is None:
                    best_path = old_path_object
                else:
                    if best_path.length > old_path_object.length:
                        best_path = old_path_object
            else:
                if not connection in old_path: #only do if no repeat
                    next_path = copy.copy(old_path)
                    next_path.append(connection)
                    if not isinstance(next_path, list):
                        print next_path
                        raise Exception
                    path_object = path_list(graph, next_path)
                    this = data_node(path_object)
                    queue.add_data_node(this)

        # check if next thing is empty. If so, terminate loop, else keep searching
        next_up = queue.get_next()
        if next_up is None:
            print "Ending the Loop"
            go = False

    if best_path is None:
        return []
    else:
        return best_path.path


## Once you have completed the breadth-first search,
## this part should be very simple to complete.
def dfs(graph, start, goal):
    raise NotImplementedError


## Now we're going to add some heuristics into the search.
## Remember that hill-climbing is a modified version of depth-first search.
## Search direction should be towards lower heuristic values to the goal.
def hill_climbing(graph, start, goal):
    raise NotImplementedError

## Now we're going to implement beam search, a variation on BFS
## that caps the amount of memory used to store paths.  Remember,
## we maintain only k candidate paths of length n in our agenda at any time.
## The k top candidates are to be determined using the
## graph get_heuristic function, with lower values being better values.
def beam_search(graph, start, goal, beam_width):
    raise NotImplementedError

## Now we're going to try optimal search.  The previous searches haven't
## used edge distances in the calculation.

## This function takes in a graph and a list of node names, and returns
## the sum of edge lengths along the path -- the total distance in the path.
def path_length(graph, node_names):
    raise NotImplementedError


def branch_and_bound(graph, start, goal):
    raise NotImplementedError

def a_star(graph, start, goal):
    raise NotImplementedError


## It's useful to determine if a graph has a consistent and admissible
## heuristic.  You've seen graphs with heuristics that are
## admissible, but not consistent.  Have you seen any graphs that are
## consistent, but not admissible?

def is_admissible(graph, goal):
    raise NotImplementedError

def is_consistent(graph, goal):
    raise NotImplementedError

HOW_MANY_HOURS_THIS_PSET_TOOK = ''
WHAT_I_FOUND_INTERESTING = ''
WHAT_I_FOUND_BORING = ''