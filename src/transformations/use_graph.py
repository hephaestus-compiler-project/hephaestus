"""node format: (namespace, variable_name)
"""


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


# TODO Add option for boolean_dict and if there is a flow from a false then
# make the node false
def check_vertices(vertices, graph):
    """Check if the given vertices can reach a None node or if a None node
    can reach the vertices.

    Returns:
        dict: vertex -> bool"""
    # TODO optimize
    none_vertices = [v for v in graph.keys() if "None" in v[1]]
    res = {v: True for v in vertices}
    for v in vertices:
        for vn in none_vertices:
            if bool(reachable(graph, v, vn) or reachable(graph, vn, v)):
                res[v] = False
    return res


def find_var_parent(graph, variable_name, current_namespace):
    """Find the parent node of a variable based on the scope.
    """
    parent_node = None
    namespace_similarity = 0
    for gnode in graph.keys():
        if gnode[1] == variable_name:
            *_, similarity = (i for i in range(0, len(current_namespace)-1)
                              if gnode[0][:i] == current_namespace[:i])
            if similarity > namespace_similarity:
                parent_node = gnode
                namespace_similarity = similarity
    return parent_node


def find_longest_paths(graph, vertex):
    def exist(x, y):
        """Checks if x is in y with the same order"""
        return x == y[:len(y)-len(x)+1]
    paths = find_all_paths(graph, vertex)
    if len(paths) == 1:
        return paths
    return [x for x in paths if not any(exist(x, p) for p in paths)]
