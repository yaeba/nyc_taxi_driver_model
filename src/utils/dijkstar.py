# Reference
# https://github.com/wylee/Dijkstar

###############################################################################
# Created 2004-12-28.
#
# Dijkstra/A* path-finding functions.
#
# Copyright (C) 2004-2007, 2012 Wyatt Baldwin. All rights reserved.
#
# Licensed under the MIT license.
#
#    http://www.opensource.org/licenses/mit-license.php
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###############################################################################



###############################################################################
## graph.py

import collections
import marshal

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle


class Graph(collections.MutableMapping):

    """A very simple graph type.

    Its structure looks like this::

        {u: {v: e, ...}, ...}  # Node v is a adjacent to u via edge e

    Edges can be of any type. Nodes have to be hashable since they're
    used as dictionary keys. ``None`` should *not* be used as a node.

    """

    def __init__(self, data=None):
        self._data = {}
        self._incoming = collections.defaultdict(dict)
        if data is not None:
            self.update(data)

    def __getitem__(self, u):
        """Get neighbors of node ``u``."""
        return self._data[u]

    def __setitem__(self, u, neighbors):
        """Set neighbors for node ``u``.

        This completely replaces ``u``'s current neighbors if ``u`` is
        already present.

        Also clears ``u``'s incoming list and updates the incoming list
        for each of the nodes in ``neighbors`` to include ``u``.

        To add an edge to an existing node, use :meth:`add_edge`
        instead.

        ``neighbors``
            A mapping of the nodes adjacent to ``u`` and the edges that
            connect ``u`` to those nodes: {v1: e1, v2: e2, ...}.

        """
        if u in self:
            del self[u]
        self._data[u] = neighbors
        for v, edge in neighbors.items():
            self._incoming[v][u] = edge

    def __delitem__(self, u):
        """Remove node ``u``."""
        del self._data[u]
        del self._incoming[u]
        for incoming in self._incoming.values():
            if u in incoming:
                del incoming[u]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def add_edge(self, u, v, edge=None):
        """Add an ``edge`` from ``u`` to ``v``."""
        if u in self:
            neighbors = self[u]
            neighbors[v] = edge
            self._incoming[v][u] = edge
        else:
            self[u] = {v: edge}

    def add_node(self, u, neighbors=None):
        """Add the node ``u``.

        This simply delegates to :meth:`__setitem__`. The only
        difference between this and that is that ``neighbors`` isn't
        required when calling this.

        """
        self[u] = neighbors if neighbors is not None else {}

    def get_incoming(self, v):
        return self._incoming[v]

    @classmethod
    def _read(cls, reader, from_):
        """Read from path or open file using specified reader."""
        if isinstance(from_, str):
            with open(from_, 'rb') as fp:
                neighbors = reader(fp)
        else:
            neighbors = reader(from_)
        return cls(neighbors)

    def _write(self, writer, to):
        """Write to path or open file using specified writer."""
        if isinstance(to, str):
            with open(to, 'wb') as fp:
                writer(self._data, fp)
        else:
            writer(self._data, to)

    @classmethod
    def load(cls, from_):
        """Read graph using pickle."""
        return cls._read(pickle.load, from_)

    def dump(self, to):
        """Write graph using pickle."""
        self._write(pickle.dump, to)

    @classmethod
    def unmarshal(cls, from_):
        """Read graph using marshal.

        Marshalling is quite a bit faster than pickling, but only the
        following types are supported: booleans, integers, long
        integers, floating point numbers, complex numbers, strings,
        Unicode objects, tuples, lists, sets, frozensets, dictionaries,
        and code objects.

        """
        return cls._read(marshal.load, from_)

    def marshal(self, to):
        """Write graph using marshal."""
        self._write(marshal.dump, to)


###############################################################################
## algorithm.py

"""Dijkstra/A* path-finding functions."""
from collections import namedtuple
from heapq import heappush, heappop
from itertools import count


PathInfo = namedtuple('PathInfo', ('nodes', 'edges', 'costs', 'total_cost'))


class DijkstarError(Exception):
    """Base class for Dijkstar errors."""


class NoPathError(DijkstarError):
    """Raised when a path can't be found to a specified node."""


def find_path(graph, s, d, annex=None, cost_func=None, heuristic_func=None):
    """Find the shortest path from ``s`` to ``d`` in ``graph``.

    Returns ordered path data. For details, see
    :func:`extract_shortest_path_from_predecessor_list`.

    """
    predecessors = single_source_shortest_paths(
        graph, s, d, annex, cost_func, heuristic_func)
    return extract_shortest_path_from_predecessor_list(predecessors, d)


def single_source_shortest_paths(graph, s, d=None, annex=None, cost_func=None,
                                 heuristic_func=None):
    """Find path from node ``s`` to all other nodes or just to ``d``.

    ``graph``
        A simple adjacency matrix (see :class:`dijkstra.graph.Graph`).
        Other than the structure, no other assumptions are made about
        the types of the nodes or edges in the graph. As a simple
        special case, if ``cost_func`` isn't specified, edges will be
        assumed to be simple numeric values.

    ``s``
        Start node.

    ``d``
        Destination node. If ``d`` is not specified, the algorithm is
        run normally (i.e., the paths from ``s`` to all reachable nodes
        are found). If ``d`` is specified, the algorithm is stopped when
        a path to ``d`` has been found.

    ``annex``
        Another ``graph`` that can be used to augment ``graph`` without
        altering it.

    ``cost_func``
        A function to apply to each edge to modify its base cost. The
        arguments it will be passed are the current node, a neighbor of
        the current node, the edge that connects the current node to
        that neighbor, and the edge that was previously traversed to
        reach the current node.

    ``heuristic_func``
        A function to apply at each iteration to help the poor dumb
        machine try to move toward the destination instead of just any
        and every which way. It gets passed the same args as
        ``cost_func``.

    return
        - Predecessor map {v => (u, e, cost to traverse e), ...}

    """
    counter = count()

    # Current known costs of paths from s to all nodes that have been
    # reached so far. Note that "reached" is not the same as "visited".
    costs = {s: 0}

    # Predecessor map for each node that has been reached from ``s``.
    # Keys are nodes that have been reached; values are tuples of
    # predecessor node, edge traversed to reach predecessor node, and
    # cost to traverse the edge from the predecessor node to the reached
    # node.
    predecessors = {s: (None, None, None)}

    # A priority queue of nodes with known costs from s. The nodes in
    # this queue are candidates for visitation. Nodes are added to this
    # queue when they are reached (but only if they have not already
    # been visited).
    visit_queue = [(0, next(counter), s)]

    # Nodes that have been visited. Once a node has been visited, it
    # won't be visited again. Note that in this context "visited" means
    # a node has been selected as having the lowest known cost (and it
    # must have been "reached" to be selected).
    visited = set()

    while visit_queue:
        # In the nodes remaining in the graph that have a known cost
        # from s, find the node, u, that currently has the shortest path
        # from s.
        cost_of_s_to_u, _, u = heappop(visit_queue)

        if u == d:
            break

        if u in visited:
            # This will happen when u has been reached from multiple
            # nodes before being visited (because multiple entries for
            # u will have been added to the visit queue).
            continue

        visited.add(u)

        if annex and u in annex:
            neighbors = annex[u]
        else:
            neighbors = graph[u] if u in graph else None

        if not neighbors:
            # u has no outgoing edges
            continue

        # The edge crossed to get to u
        prev_e = predecessors[u][1]

        # Check each of u's neighboring nodes to see if we can update
        # its cost by reaching it from u.
        for v in neighbors:
            # Don't backtrack to nodes that have already been visited.
            if v in visited:
                continue

            e = neighbors[v]

            # Get the cost of the edge running from u to v.
            cost_of_e = cost_func(u, v, e, prev_e) if cost_func else e

            # Cost of s to u plus the cost of u to v across e--this
            # is *a* cost from s to v that may or may not be less than
            # the current known cost to v.
            cost_of_s_to_u_plus_cost_of_e = cost_of_s_to_u + cost_of_e

            # When there is a heuristic function, we use a
            # "guess-timated" cost, which is the normal cost plus some
            # other heuristic cost from v to d that is calculated so as
            # to keep us moving in the right direction (generally more
            # toward the goal instead of away from it).
            if heuristic_func:
                additional_cost = heuristic_func(u, v, e, prev_e)
                cost_of_s_to_u_plus_cost_of_e += additional_cost

            if v not in costs or costs[v] > cost_of_s_to_u_plus_cost_of_e:
                # If the current known cost from s to v is greater than
                # the cost of the path that was just found (cost of s to
                # u plus cost of u to v across e), update v's cost in
                # the cost list and update v's predecessor in the
                # predecessor list (it's now u). Note that if ``v`` is
                # not present in the ``costs`` list, its current cost
                # is considered to be infinity.
                costs[v] = cost_of_s_to_u_plus_cost_of_e
                predecessors[v] = (u, e, cost_of_e)
                heappush(visit_queue, (cost_of_s_to_u_plus_cost_of_e, next(counter), v))

    if d is not None and d not in costs:
        raise NoPathError('Could not find a path from {0} to {1}'.format(s, d))

    return predecessors


def extract_shortest_path_from_predecessor_list(predecessors, d):
    """Extract ordered lists of nodes, edges, costs from predecessor list.

    ``predecessors``
        Predecessor list {u: (v, e), ...} u's predecessor is v via e

    ``d``
        Destination node

    return a ``PathInfo`` object containing:
        - nodes: The nodes on the shortest path to ``d``
        - edges: The edges on the shortest path to ``d``
        - costs: The costs of the edges on the shortest path to ``d``
        - total_cost: The total cost of the path

    The items in the ``PathInfo`` object can be accessed like a tuple
    (e.g., ``info[3]``) or an object (e.g., ``info.total_cost``).

    """
    nodes = [d]  # Nodes on the shortest path from s to d
    edges = []   # Edges on the shortest path from s to d
    costs = []   # Costs of the edges on the shortest path from s to d
    u, e, cost = predecessors[d]
    while u is not None:
        # u is the node from which v was reached, e is the edge
        # traversed to reach v from u, and cost is the cost of u to
        # v over e. (Note that v is implicit--it's the previous u).
        nodes.append(u)
        edges.append(e)
        costs.append(cost)
        u, e, cost = predecessors[u]
    nodes.reverse()
    edges.reverse()
    costs.reverse()
    total_cost = sum(costs)
    return PathInfo(nodes, edges, costs, total_cost)
