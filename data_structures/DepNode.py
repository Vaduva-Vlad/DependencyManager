from PackageReader import PackageReader
class DepNode:
    def __init__(self, pkg, version=None):
        self.children = []
        self.pkg_name,self.version_reqs = PackageReader.get_version_reqs(pkg)
        self.parents=[]
        self.version=version

    def add_child(self, child):
        child.pkg_name="_".join(child.pkg_name.split('-'))
        child.parents.append(self)
        self.children.append(child)
        return child

    def set_version(self,version):
        self.version=version

if __name__=="__main__":
    node=DepNode('numpy >= 1.23.2; python_version == "3.11"')
    node.add_child('numpy >= 1.23.2; python_version == "3.11"')
    print(node.children[0].parent)