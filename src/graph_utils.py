from src.analysis.use_analysis import NONE_NODE


class Node(object):
    def is_none(self):
        raise NotImplementedError("is_none must be implemented")


def reachable(graph, start_vertex, dest_vertex):
    """Find if a start_vertex can reach dest_vertex with BFS."""
    visited = {v: False for v in graph.keys()}

    queue = []
    queue.append(start_vertex)
    if start_vertex not in visited:
        return False
    visited[start_vertex] = True

    while queue:
        next_v = queue.pop(0)

        if next_v == dest_vertex:
             return True

        for v in graph[next_v]:
            if v in visited and visited[v] == False:
                queue.append(v)
                visited[v] = True
    return False


def bi_reachable(graph, start_vertex, dest_vertex):
    """Bidirectional reachable"""
    return (reachable(graph, start_vertex, dest_vertex) or
            reachable(graph, dest_vertex, start_vertex))


def connected(graph, start_vertex, dest_vertex):
    """Find if a start_vertex can connect to dest_vertex.

    The following example is neither reachable nor bi-reachable, but it is
    connected:
        G: 0 -> 1 -> 2, 4 -> 2

        Connected: 4->0, 0->4, 1->4, etc. and all bi-reachable
    """
    # TODO optimize
    visited = {v: False for v in graph.keys()}

    queue = []
    queue.append(start_vertex)
    if start_vertex not in visited:
        return False
    visited[start_vertex] = True

    while queue:
        next_v = queue.pop(0)

        if next_v == dest_vertex:
             return True

        for node, adjs in graph.items():
            if next_v == node:
                for v in adjs:
                    if v in visited and visited[v] == False:
                        queue.append(v)
                        visited[v] = True
            if next_v in adjs and visited[node] == False:
                queue.append(node)
                visited[node] = True

    return False


def none_reachable(graph, vertex, none_node=NONE_NODE):
    reachable_nodes = find_all_bi_reachable(graph, vertex)
    if any(bi_reachable(graph, v, none_node) for v in reachable_nodes):
        return True
    return False


def none_connected(graph, vertex, none_node=NONE_NODE):
    connected_nodes = find_all_connected(graph, vertex)
    if any(connected(graph, v, none_node) for v in connected_nodes):
        return True
    return False


def find_all_paths(graph, start, path=[]):
    """Find all the paths of graph from start."""
    path = path + [start]
    if start not in graph:
        return [path]
    paths = [path]
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def find_longest_paths(graph, vertex):
    def exist(x, y):
        """Checks if x is in y with the same order"""
        return x == y[:len(y)-len(x)+1]
    paths = find_all_paths(graph, vertex)
    if len(paths) == 1:
        return paths
    return [x for x in paths if not any(exist(x, p) for p in paths)]


def find_all_reachable(graph, vertex):
    res = set()
    for path in find_longest_paths(graph, vertex):
        res.update(path)
    return res


# TODO optimize
def find_all_bi_reachable(graph, vertex):
    return {n for n in graph if bi_reachable(graph, vertex, n)}


# TODO optimize
def find_all_connected(graph, vertex):
    return {n for n in graph if connected(graph, vertex, n)}
