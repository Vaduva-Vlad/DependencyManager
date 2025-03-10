import os
import requests
from ProjectInfo import ProjectInfo
import re
from packaging.version import Version
from data_structures.operator_lookup_table import op
from data_structures.DependencyTree import DependencyTree
from data_structures.DepNode import DepNode


class DependencyManager:
    def __init__(self, project_path, project_info, installed_packages=None):
        self.project_path = project_path
        self.metadata_buffer = []
        self.project_info = project_info
        self.dep_tree = None
        self.installed_packages = installed_packages

    def get_installed_package_dependencies(self, package, type='all'):
        self.metadata_buffer = self.get_metadata(package)

        dependencies = []
        for row in self.metadata_buffer:
            if row.startswith("Requires-Dist"):
                trimmed_row = row.split(' ', 1)[1].strip()
                dependencies.append(trimmed_row)
        match type:
            case 'all':
                return dependencies

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

    def build_branches(self, current_node, pkg_name, version, tree):
        dependencies=self.get_installed_package_dependencies('-'.join([pkg_name,version]))

        dependencies = self.filter_by_installable(dependencies)
        if len(dependencies) == 0:
            return
        for dependency in dependencies:
            node=current_node.add_child(dependency)
            if node.pkg_name not in self.installed_packages.keys():
                print('here')

    def build_dep_tree(self, package_name, version):
        root = DepNode(package_name, version)
        tree = DependencyTree(root)
        self.build_branches(root,package_name, version, tree)
        pass

if __name__ == "__main__":
    p_info = ProjectInfo()
    d = DependencyManager('C:/Users/vland/source/repos/depmanagertestproject', p_info,{'blinker': '1.9.0', 'click': '8.1.7', 'colorama': '0.4.6', 'flask': '3.1.0', 'itsdangerous': '2.2.0', 'jinja2': '3.1.4', 'MarkupSafe': '3.0.2', 'numpy': '2.1.3', 'pandas': '2.2.3', 'python_dateutil': '2.9.0.post0', 'pytz': '2024.2', 'six': '1.16.0', 'tzdata': '2024.2', 'werkzeug': '3.1.3'})
    # data = d.get_installed_package_dependencies('pandas-2.2.3')
    # data = d.get_dependencies_pypi('requests')
    # c = d.filter_by_installable(data)
    # print(c)
    d.build_dep_tree('pandas','2.2.3')