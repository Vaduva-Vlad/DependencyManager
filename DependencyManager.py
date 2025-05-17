import os
import requests

from PackageReader import PackageReader
from ProjectInfo import ProjectInfo
import re
from packaging.version import Version
from data_structures.operator_lookup_table import op
from data_structures.DependencyTree import DependencyTree
from data_structures.DepNode import DepNode
from collections import defaultdict


class DependencyManager:
    def __init__(self, project_path, project_info, package_reader):
        self.project_path = project_path
        self.metadata_buffer = []
        self.project_info = project_info
        self.package_reader = package_reader
        self.installed_packages = self.package_reader.read_installed_packages()
        self.dep_trees = self.build_dep_tree()

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
        info = re.findall(r"(python_version)|(>=|<=|==|<|>)|\"(.*?)\"|\'(.*?)\'", dependency)
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
            dependency_names.append(name.lower())
        return dependency_names

    def identify_parent(self, nodes, reqs):
        for node in nodes:
            if node.version_reqs == reqs:
                return node

    def build_branches(self, current_node, discovered_packages, local=True):
        if local:
            dependencies = self.get_installed_package_dependencies(
                '-'.join([current_node.pkg_name, current_node.version]))
        else:
            dependencies = self.get_dependencies_pypi(current_node.pkg_name, current_node.version)
        # TODO: update to filter by OS!!
        dependencies = self.filter_by_installable(dependencies)
        dependency_names = self.get_dep_names(dependencies)
        if len(dependencies) == 0:
            return

        dep_dict = {}
        for dependency in dependencies:
            name, version_req = PackageReader.get_version_reqs(dependency)
            name = '_'.join(name.split('-'))
            name = name.lower()
            dep_dict[name] = version_req

        for package in self.installed_packages.keys():
            if package.lower() not in dependency_names:
                continue
            node = DepNode(package, self.installed_packages[package], dep_dict[package.lower()])
            version = PackageReader.get_installed_version(node.pkg_name, self.project_path)
            node.set_version(version)

            # If true, the package has been found as a dependency before, for another package
            if not self.is_package_discovered(node, discovered_packages):
                discovered_packages[package].append(node)
                self.build_branches(node, discovered_packages)
            else:
                node = self.identify_parent(discovered_packages[package], dep_dict[package.lower()])
            current_node.add_child(node)

    def build_dep_tree(self):
        discovered_packages = defaultdict(list)
        for package in self.installed_packages.keys():
            version = self.installed_packages[package]
            node = DepNode(package, version)
            if not self.is_package_discovered(node, discovered_packages):
                discovered_packages[node.pkg_name].append(node)
            self.build_branches(node, discovered_packages, True)

        self.find_root_packages(discovered_packages)
        trees=[]
        for root in discovered_packages:
            for node in discovered_packages[root]:
                trees.append(DependencyTree(node))
        return trees

    def is_package_discovered(self, package_node, discovered_packages):
        if package_node.pkg_name not in discovered_packages.keys():
            return False
        else:
            if package_node.version_reqs is None:
                return True
        discovered = discovered_packages[package_node.pkg_name]
        for node in discovered:
            if node.version_reqs is None:
                node.version_reqs = package_node.version_reqs
            if node.version_reqs == package_node.version_reqs:
                return True
        return False

    def find_root_packages(self, pkg_dict):
        packages = pkg_dict.copy()
        for pkg_name in packages:
            node_list = pkg_dict[pkg_name]
            node = 0
            while node < len(node_list):
                if len(node_list[node].parents) != 0:
                    node_list.pop(node)
                else:
                    node += 1
            if len(node_list) == 0:
                pkg_dict.pop(pkg_name, None)

    def find_mismatched_versions(self, current_node, bad_packages):
        dependencies = current_node.children
        if len(dependencies) == 0:
            return {}

        for dependency in dependencies:
            installed_version = Version(dependency.version)

            operator = dependency.version_reqs["operator"]
            required_version = Version(dependency.version_reqs["version"])
            version_matches = op[operator](installed_version, required_version)
            if not version_matches:
                    bad_packages[dependency.pkg_name].append(dependency)
            self.find_mismatched_versions(dependency, bad_packages)

    def find_parents(self, node, package_name, result):
        for child in node.children:
            if child.pkg_name==package_name:
                result.append({"parent": node,"child":child})

    def get_packages_with_dependency(self, dependency):
        parents=[]
        for tree in self.dep_trees:
            tree.traverse(tree.root,self.find_parents,[dependency,parents])
        return parents

    def get_version_ranges(self, dependency, current_node, packages=[]):
        if len(current_node.children) == 0:
            return
        for child in current_node.children:
            if child.pkg_name == dependency:
                packages.append((child.version_reqs["operator"], child.version_reqs["version"]))
            self.get_version_ranges(dependency, child, packages)

    def find_common_version(self, dependency_name, version_ranges):
        releases = PackageReader.get_all_package_releases(dependency_name)

        for pair in version_ranges:
            releases = PackageReader.filter_release_list(releases, pair[0], Version(pair[1]))
        return releases

    def validate_version(self, current_node, version, incompatible_packages={}):
        parents=self.get_packages_with_dependency(current_node.pkg_name)
        for parent in parents:
            child=parent['child']
            operator=child.version_reqs["operator"]
            child_version=Version(child.version_reqs["version"])
            if not op[operator](version,child_version):
                incompatible_packages[parent["parent"].pkg_name]=(child.pkg_name,child.version_reqs)
        for child in current_node.children:
            self.validate_version(child, Version(child.version),incompatible_packages)

    def diagnose_versions(self):
        version_problems=defaultdict(list)
        for tree in self.dep_trees:
            self.find_mismatched_versions(tree.root,version_problems)

        for dependency in version_problems.keys():
            version_ranges=[]
            for tree in self.dep_trees:
                self.get_version_ranges(dependency,tree.root, version_ranges)
            common_versions = self.find_common_version(dependency, version_ranges)
            new_version = max(common_versions)
            new_branches = DepNode(dependency, str(new_version))
            self.build_branches(new_branches, defaultdict(list), False)
            new_subtree = DependencyTree(new_branches)
            incompatible_packages={}
            self.validate_version(new_subtree.root, new_version,incompatible_packages)
            pass

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


if __name__ == "__main__":
    p_path = ''
    p_info = ProjectInfo()
    p_reader = PackageReader(p_path)
    d = DependencyManager(p_path, p_info, p_reader)
    d.diagnose_versions()
    d.validate_version('pandas',"2.2.2")
    d.get_packages_with_dependency('numpy')
