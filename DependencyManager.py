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
        data = data if data is not None else []
        return [dep for dep in data if "extra ==" not in dep]

    def get_latest_version_info_pypi(self, package):
        url = f"https://pypi.org/pypi/{package}/json"
        version = requests.get(url).json()['info']['version']
        return Version(version)

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

    def get_dep_names(self, dependencies):
        dependency_names = []
        for dependency in dependencies:
            name = PackageReader.get_package_name(dependency)
            name = '_'.join(name.split('-'))
            dependency_names.append(name)
        return dependency_names

    def build_branches(self, current_node, discovered_packages={}, local=True):
        if local:
            dependencies = self.get_installed_package_dependencies(
                '-'.join([current_node.pkg_name, current_node.version]))
        else:
            dependencies = self.get_dependencies_pypi(current_node.pkg_name, current_node.version)
        dependencies = self.filter_by_installable(dependencies)
        dependency_names = self.get_dep_names(dependencies)
        if len(dependencies) == 0:
            return

        dep_dict = {}
        for dependency in dependencies:
            name, version_req = PackageReader.get_version_reqs(dependency)
            name = '_'.join(name.split('-'))
            dep_dict[name] = version_req

        for package in self.installed_packages.keys():
            if package not in dependency_names:
                continue
            node = DepNode(package, self.installed_packages[package], dep_dict[package])
            version = PackageReader.get_installed_version(node.pkg_name, self.project_path)
            node.set_version(version)

            # If true, the package has been found as a dependency before, for another package
            if package not in discovered_packages.keys() or discovered_packages[package].version_reqs != node.version:
                discovered_packages[package] = node
                self.build_branches(node, discovered_packages)
            else:
                node = discovered_packages[package]
                node.parents.append(current_node)
            current_node.add_child(node)

    def build_dep_tree(self, package_name, version, local=True):
        root = DepNode(package_name, version)
        tree = DependencyTree(root)
        self.build_branches(root, {}, local)
        self.dep_tree = tree
        tree.print_tree(tree.root)

    def find_mismatched_versions(self, current_node, bad_packages={}):
        dependencies = current_node.children
        if len(dependencies) == 0:
            return

        for dependency in dependencies:
            installed_version = Version(dependency.version)

            operator = dependency.version_reqs["operator"]
            required_version = Version(dependency.version_reqs["version"])
            version_matches = op[operator](installed_version, required_version)
            if not version_matches:
                if dependency.pkg_name in bad_packages:
                    bad_packages[dependency.pkg_name].append(dependency)
                else:
                    bad_packages[dependency.pkg_name] = [dependency]
            self.find_mismatched_versions(dependency, bad_packages)
        return bad_packages

    def get_version_ranges(self, dependency, current_node, packages=[]):
        if len(current_node.children) == 0:
            return
        for child in current_node.children:
            if child.pkg_name == dependency:
                packages.append((child.version_reqs["operator"], child.version_reqs["version"]))
            self.get_version_ranges(dependency, child, packages)
        return packages

    def find_common_version(self, dependency_name, version_ranges):
        releases = PackageReader.get_all_package_releases(dependency_name)

        for pair in version_ranges:
            releases = PackageReader.filter_release_list(releases, pair[0], Version(pair[1]))
        return releases

    def validate_version(self,package_name, version):
        new_branches=DepNode(package_name, str(version))
        self.build_branches(new_branches,{}, False)
        pass

    def diagnose_versions(self):
        version_problems = self.find_mismatched_versions(self.dep_tree.root)
        for dependency in version_problems.keys():
            version_ranges = self.get_version_ranges(dependency, self.dep_tree.root)
            common_versions = self.find_common_version(dependency, version_ranges)
            new_version=max(common_versions)
            self.validate_version(dependency, new_version)

    def check_for_missing_dependencies(self, current_node, missing_dependencies={}):
        dependencies = self.get_installed_package_dependencies('-'.join([current_node.pkg_name, current_node.version]))
        dependencies = self.filter_by_installable(dependencies)

        if len(dependencies) == 0:
            return

        for dependency in dependencies:
            name, reqs = PackageReader.get_version_reqs(dependency)
            name = '_'.join(name.split('-'))
            if name not in self.installed_packages.keys():
                missing_dependencies[name] = reqs

        for child in current_node.children:
            self.check_for_missing_dependencies(child, missing_dependencies)
        return missing_dependencies

    def traverse_tree(self,current_node,func,args):
        pass

if __name__ == "__main__":
    p_path = 'C:/Users/vland/source/repos/depmanagertestproject'
    p_info = ProjectInfo()
    p_reader = PackageReader(p_path)
    d = DependencyManager(p_path, p_info, p_reader)
    d.build_dep_tree('pandas', '2.2.3', True)
    pass
    #print(d.check_for_missing_dependencies(d.dep_tree.root))
    #d.diagnose_versions()
    d.validate_version('python-dateutil',"2.8.2")