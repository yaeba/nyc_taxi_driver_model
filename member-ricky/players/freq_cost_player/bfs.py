import pandas as pd
import dijkstar
from collections import deque


def prepare_graph(cells_file):
    '''
    Create a Graph object from a file containing all cells' id

    :param str cells_file: Path to the cells file
    :return: A graph object
    '''
    cells = pd.read_csv(cells_file, header=None, names=['id'])
    cells = cells['id']\
        .str.split(':')\
        .apply(lambda x: tuple([int(x[0]), int(x[1])])).tolist()

    graph = dijkstar.Graph()

    for cell in cells:
        poss_neighbour = [(cell[0]+i, cell[1]+j)
                          for i in [-1, 0, 1] for j in [-1, 0, 1]]
        for neighbour in poss_neighbour:
            if neighbour in cells:
                graph.add_edge(cell, neighbour, {'cost': 1})

    return graph


def save_graph(graph, graph_file):
    '''
    Save the graph to a pickled object

    :param Graph graph: Graph object to be saved
    :param str graph_file: Output graph pickled file
    '''
    graph.dump(graph_file)


def load_graph(graph_file):
    '''
    Load saved graph object

    :param str graph_file: Saved graph object to be loaded
    '''
    return dijkstar.Graph.load(graph_file)


def bfs(graph, start):
    '''
    Compute costs to all reachable destinations (BFS with cost 1)

    :param Graph graph: Graph object to operate on
    :param str start: Origin cell id (eg "24:105")
    :return: Dictionary containing costs to all reachable cells
    '''
    start = to_tuple(start)
    costs = {start: 0}

    visit_queue = deque([start])
    visited = set()

    while visit_queue:
        node = visit_queue.popleft()
        visited.add(node)

        for neighbour in graph[node].keys():
            if neighbour not in visited and neighbour not in visit_queue:
                costs[neighbour] = costs[node] + 1
                visit_queue.append(neighbour)

    return {to_cell_id(k): v for (k, v) in costs.items()}


def find_shortest_path(graph, start, dest):
    '''
    Find shortest path from one cell to another (BFS with cost 1)

    :param Graph graph: Graph object to operate on
    :param str start: Origin cell id (eg "24:105")
    :param str dest: Destination cell id (eg "26:107")
    :return: List of nodes in path
    :raise NoPathError: When dest is not reachable from start
    '''
    def cost_func(u, v, e, prev_e): return e['cost']
    start = to_tuple(start)
    dest = to_tuple(dest)
    path = dijkstar.find_path(graph, start, dest, cost_func=cost_func)[0]
    return list(map(to_cell_id, path))


# Helper function to convert cell from id (str) to tuple form
def to_tuple(cell):
    return tuple(map(int, cell.split(':')))

# Helper function to convert cell from tuple to id (str) form


def to_cell_id(cell_tuple):
    return ':'.join(map(str, cell_tuple))
