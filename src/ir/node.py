class Node(object):

    def accept(self, visitor):
        return visitor.visit(self)

    def children(self):
        raise NotImplementedError('children() must be implemented')

    def update_children(self, children):
        assert len(children) == len(self.children()), (
            'The number of the given children is not compatible'
            ' with the number of the node\'s children.')
