import os
import requests
from ProjectInfo import ProjectInfo
import re
from packaging.version import Version
from data_structures.operator_lookup_table import op


class DependencyManager:
    def __init__(self, project_path, project_info):
        self.project_path = project_path
        self.metadata_buffer = []
        self.project_info = project_info

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

    def get_dependencies_pypi(self, package, type='all'):
        url = f"https://pypi.org/pypi/{package}/json"
        data = requests.get(url).json()['info']['requires_dist']
        return data

    def get_metadata(self, package):
        metadata_path = os.path.join(self.project_path, '.venv', 'Lib', 'site-packages', f"{package}.dist-info",
                                     "METADATA")
        with open(metadata_path, "r") as metadata:
            contents = metadata.readlines()

        return contents

    def get_py_dep_reqs(self, dependency):
        info = re.findall(r"(python_version)|(>=|<=|==|<|>)|\"(.*?)\"", dependency)
        info = [tuple(filter(None, item)) for item in info]
        results = [r for tup in info for r in tup]
        operators = []
        for result in range(len(results)):
            if results[result] == 'python_version':
                operators.append(results[result + 1])
                version = results[result + 2]
                # if results[result + 3] in op.keys():
                #     operators.append(results[result + 3])
                return operators, version

    def is_py_compatible(self, dependency):
        python_version = self.project_info.get_python_version(self.project_path)
        operators, version = self.get_py_dep_reqs(dependency)
        python_version = Version(python_version)
        version = Version(version)
        if len(operators)==1:
            return op[operators[0]](python_version, version)
        return op[operators[0]](python_version, version) and op[operators[1]](python_version, version)

    def filter_by_py_version(self, dependencies):
        filtered_dependencies = dependencies.copy()
        for dependency in dependencies:
            if 'python_version' in dependency and not self.is_py_compatible(dependency):
                filtered_dependencies.remove(dependency)
        return filtered_dependencies

    def filter_by_installable(self, dependencies):
        return self.filter_by_py_version(dependencies)


if __name__ == "__main__":
    p_info = ProjectInfo()
    d = DependencyManager('C:/Users/vland/source/repos/depmanagertestproject', p_info)
    # print(d.get_all_installed_package_dependencies('pandas-2.2.3'))
    data = d.get_dependencies_pypi('pandas')
    c = d.filter_by_installable(data)
    print(c)
