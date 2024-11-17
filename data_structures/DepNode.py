import re
class DepNode:
    def __init__(self, pkg_name, version_reqs=None):
        self.parent = None
        self.children = []
        self.pkg_name = pkg_name
        self.version_reqs=version_reqs
        self.parent=None
        self.installed_version=None

    def __get_version_info(self,dependency):
        #info=re.findall(r"(.*)(<=|>=|==|>|<)((\s*[\d\.]+\d(post|dev|pre)*)[0-9]*)",dependency)
        dependency = dependency.split(';')[0]
        info = re.findall(r"^[^<=|>=|==|>|<]*(<=|>=|==|>|<)(.*)$", dependency)
        info = [tuple(filter(None, item)) for item in info]
        results = [r.strip() for tup in info for r in tup]
        results = "".join(results)
        pkg_name = dependency.split(results[0])[0]
        if '(' in pkg_name:
            pkg_name = pkg_name.split('(')[0]
        pkg_name = pkg_name.strip()
        if ')' in results:
            results = results.split(')')[0]

        results=results.split(',')
        reqs={}
        for result in results:
            comp_and_version=re.findall(r"(<=|>=|==|>|<)(.*)",result)
            comp_and_version=[i for i in comp_and_version[0]]
            comp=comp_and_version[0]
            version=comp_and_version[1]
            reqs[comp]=version
        return pkg_name, reqs

    def add_child(self, dependency):
        pkg_name,reqs=self.__get_version_info(dependency)
        child=DepNode(pkg_name, reqs)
        child.parent=self
        self.children.append(child)

if __name__=="__main__":
    node=DepNode('pandas')
    node.add_child('numpy >= 1.23.2; python_version == "3.11"')
    print(node.children[0].parent)