import os
import requests
from ProjectInfoSingleton import ProjectInfo
import re

class DependencyManager():
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
        self.filter_by_py_version(data)

    def get_metadata(self, package):
        metadata_path = os.path.join(self.project_path, '.venv', 'Lib', 'site-packages', f"{package}.dist-info",
                                     "METADATA")
        with open(metadata_path, "r") as metadata:
            contents = metadata.readlines()

        return contents

    def is_py_compatible(self,dependency):
        python_version = self.project_info.get_python_version(self.project_path)
        info=re.findall(r"python_version|>=|<=|==|<|>|(?<=\"|').*?(?=\"|')",dependency)
        for result in range(len(info)):
            if info[result] == 'python_version':
                comp_operator=info[result+1]
                version=info[result+2]
                break
        pass

    def filter_by_py_version(self, dependencies):

        filtered_dependencies = []
        for dependency in dependencies:
            if 'python_version' in dependency:
                self.is_py_compatible(dependency)

if __name__ == "__main__":
    p_info = ProjectInfo()
    d = DependencyManager('C:/Users/vland/source/repos/depmanagertestproject', p_info)
    # print(d.get_all_installed_package_dependencies('pandas-2.2.3'))
    print(d.get_dependencies_pypi('pandas'))
