from data_structures.DepNode import DepNode


class DependencyTree:
    def __init__(self, root):
        self.root = root
        self.has_cycle = False

    def find_cycle(self, node, visited=[], path=[]):
        if node in path:
            self.has_cycle = True
        if node not in visited:
            visited.append(node)
            path.append(node)
            for child in node.children:
                self.find_cycle(child, visited, path)
            path.pop()

    def print_tree(self, node, level=0, visited=[], path=[]):
        if self.has_cycle:
            return
        if node.version_reqs is not None:
            print("  " * level, node.pkg_name, node.version_reqs['operator'], node.version_reqs['version'])
        else:
            print("  " * level, node.pkg_name)
        visited.append(node)
        path.append(node)
        for child in node.children:
            self.print_tree(child, level + 1, visited, path)
        path.pop()

    #Traverse the tree and run a function for each node
    def traverse(self, node, func, args):
        if self.has_cycle:
            return
        func(node, *args)
        for child in node.children:
            self.traverse(child, func, args)

if __name__ == "__main__":
    # root = DepNode('5')
    # n2 = DepNode('2')
    # n3 = DepNode('3')
    # n4 = DepNode('4')
    # n8 = DepNode('8')
    # n7 = DepNode('7')
    #
    # # n2.children.append(root)
    # n3.children.append(n2)
    # n3.children.append(n4)
    # n4.children.append(n8)
    # n7.children.append(n8)
    # root.children.append(n3)
    # root.children.append(n7)
    # t = DependencyTree(root)

    root = DepNode('A')
    b = DepNode('B')
    c = DepNode('C')
    d = DepNode('D')
    e = DepNode('E')
    root.children.append(b)
    root.children.append(d)
    b.children.append(c)
    # c.children.append(d)
    d.children.append(c)
    # c.children.append(b)
    t = DependencyTree(root)
    t.traverse(t.root)
