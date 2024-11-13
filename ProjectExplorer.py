from exceptions.PackageNotInstalledException import PackageNotInstalledException

from DependencyManager import DependencyManager
from PackageReader import PackageReader


class ProjectExplorer():
    def __init__(self, project_path):
        self.project_path = project_path
        self.package_reader=PackageReader(project_path)
        self.dependency_manager=DependencyManager(project_path)

    def get_all_dependencies(self,package_name):
        installed_packages=self.package_reader.read_packages()
        if package_name not in installed_packages:
            raise PackageNotInstalledException()
        package_version=installed_packages[package_name]
        full_pkg_name=f"{package_name}-{package_version}"
        return self.dependency_manager.get_all_installed_package_dependencies(full_pkg_name)


if __name__ == '__main__':
    p=ProjectExplorer('C:/Users/vland/source/repos/depmanagertestproject')
    p.get_all_dependencies('pandas')