"""node format: (namespace: tuple, name: str)
"""


def reachable(graph, start_vertex, dest_vertex):
    """Find if a start_vertex can reach dest_vertex with BFS."""
    visited = {v: False for v in graph.keys()}

    queue = []
    queue.append(start_vertex)
    visited[start_vertex] = True

    while queue:
        next_v = queue.pop(0)

        if next_v == dest_vertex:
             return True

        for v in graph[next_v]:
            if visited[v] == False:
                queue.append(v)
                visited[v] = True
    return False


def bi_reachable(graph, start_vertex, dest_vertex):
    """Bidirectional reachable"""
    return (reachable(graph, start_vertex, dest_vertex) or
            reachable(graph, dest_vertex, start_vertex))


def none_reachable(graph, vertex):
    """Check if vertex is bi_reachable from/to a none vertex
    """
    none_vertices = [v for v in graph.keys() if v[1] is None]
    for nv in none_vertices:
        if bi_reachable(graph, vertex, nv):
            return True
    return False


def find_all_paths(graph, start, path=[]):
    """Find all the paths of graph."""
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
