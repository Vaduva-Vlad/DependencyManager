from DependencyManager import DependencyManager
from PackageReader import PackageReader


class ProjectExplorer():
    def __init__(self, project_path):
        self.project_path = project_path
        self.package_reader=PackageReader(project_path)
        self.dependency_manager=DependencyManager(project_path)

    def get_dependencies(self,package_name):
        installed_packages=self.package_reader.read_packages()
        if package_name not in installed_packages:


if __name__ == '__main__':
    p=ProjectExplorer('C:/Users/vland/source/repos/depmanagertestproject')
    p.package_reader.read_packages()