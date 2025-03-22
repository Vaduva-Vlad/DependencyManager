import os
import requests

from PackageReader import PackageReader
from ProjectInfo import ProjectInfo
import re
from packaging.version import Version
from data_structures.operator_lookup_table import op
from data_structures.DependencyTree import DependencyTree
from data_structures.DepNode import DepNode


class DependencyManager:
    def __init__(self, project_path, project_info, package_reader):
        self.project_path = project_path
        self.metadata_buffer = []
        self.project_info = project_info
        self.dep_tree = None
        self.package_reader = package_reader
        self.installed_packages = self.package_reader.read_installed_packages()

    def get_installed_package_dependencies(self, package, type=None):
        self.metadata_buffer = self.get_metadata(package)

        dependencies = []
        for row in self.metadata_buffer:
            if row.startswith("Requires-Dist"):
                trimmed_row = row.split(' ', 1)[1].strip()
                dependencies.append(trimmed_row)
        match type:
            case None:
                return [dep for dep in dependencies if "extra ==" not in dep]

    def get_metadata(self, package):
        metadata_path = os.path.join(self.project_path, '.venv', 'Lib', 'site-packages', f"{package}.dist-info",
                                     "METADATA")
        with open(metadata_path, "r") as metadata:
            contents = metadata.readlines()

        return contents

    def get_dependencies_pypi(self, package, version=None, type='all'):
        if version is None:
            url = f"https://pypi.org/pypi/{package}/json"
        else:
            url = f"https://pypi.org/pypi/{package}/{version}/json"
        data = requests.get(url).json()['info']['requires_dist']
        return data if data is not None else []

    def get_py_dep_reqs(self, dependency):
        info = re.findall(r"(python_version)|(>=|<=|==|<|>)|\"(.*?)\"", dependency)
        info = [tuple(filter(None, item)) for item in info]
        results = [r for tup in info for r in tup]
        reqs = {}
        for result in range(len(results)):
            if results[result] == 'python_version':
                operator = results[result + 1]
                version = results[result + 2]
                reqs[operator] = version
                # if results[result + 3] in op.keys():
                #     operators.append(results[result + 3])
                return reqs

    def is_py_compatible(self, dependency):
        python_version = self.project_info.get_python_version(self.project_path)
        reqs = self.get_py_dep_reqs(dependency)
        python_version = Version(python_version)

        for operator in reqs.keys():
            version = Version(reqs[operator])
            if not op[operator](python_version, version):
                return False
        return True

    def filter_by_py_version(self, dependencies):
        filtered_dependencies = dependencies.copy()
        for dependency in dependencies:
            if 'python_version' in dependency and not self.is_py_compatible(dependency):
                filtered_dependencies.remove(dependency)
        return filtered_dependencies

    def filter_by_installable(self, dependencies):
        return self.filter_by_py_version(dependencies)

    def get_dep_names(self,dependencies):
        dependency_names=[]
        for dependency in dependencies:
            name=PackageReader.get_package_name(dependency)
            name='_'.join(name.split('-'))
            dependency_names.append(name)
        return dependency_names

    def build_branches(self, current_node, tree, discovered_packages={}):
        dependencies=self.get_installed_package_dependencies('-'.join([current_node.pkg_name,current_node.version]))
        dependencies = self.filter_by_installable(dependencies)
        dependency_names=self.get_dep_names(dependencies)
        if len(dependencies) == 0:
            return
        for package in self.installed_packages.keys():
            if package not in dependency_names:
                continue
            node = DepNode(package, self.installed_packages[package])
            version=PackageReader.get_installed_version(node.pkg_name,self.project_path)
            node.set_version(version)
            current_node.add_child(node)
            self.build_branches(node, tree)

    def build_dep_tree(self, package_name, version):
        root = DepNode(package_name, version)
        tree = DependencyTree(root)
        self.build_branches(root, tree)
        tree.print_tree(tree.root)

if __name__ == "__main__":
    p_path='C:/Users/vland/source/repos/depmanagertestproject'
    p_info = ProjectInfo()
    p_reader = PackageReader(p_path)
    d = DependencyManager(p_path, p_info,p_reader)
    # data = d.get_installed_package_dependencies('pandas-2.2.3')
    # data = d.get_dependencies_pypi('requests')
    # c = d.filter_by_installable(data)
    # print(c)
    d.build_dep_tree('pandas','2.2.3')