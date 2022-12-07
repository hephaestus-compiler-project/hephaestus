def append_to(visit):
    def inner(self, node):
        self._nodes_stack.append(node)
        visit(self, node)
        self._nodes_stack.pop()
    return inner
