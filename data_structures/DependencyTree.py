from DepNode import DepNode


class DependencyTree:
    def __init__(self, root):
        self.root = root
        self.has_cycle = False

    def dfs(self, node, visited=[], path=[]):
        if node in path:
            self.has_cycle = True
        if node not in visited:
            print(node.pkg_name)

            visited.append(node)
            path.append(node)
            for child in node.children:
                self.dfs(child, visited, path)
            path.pop()


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


    root=DepNode('A')
    b=DepNode('B')
    c=DepNode('C')
    d=DepNode('D')

    root.children.append(b)
    root.children.append(d)
    b.children.append(c)
    #c.children.append(d)
    d.children.append(c)
    t=DependencyTree(root)
    t.dfs(t.root)
    print(t.has_cycle)
