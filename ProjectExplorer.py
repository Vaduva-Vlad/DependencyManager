from ProjectInfo import ProjectInfo
from exceptions.PackageNotInstalledException import PackageNotInstalledException

from DependencyManager import DependencyManager
from PackageReader import PackageReader


class ProjectExplorer():
    def __init__(self, project_path,project_info):
        self.project_path = project_path
        self.project_info = project_info
        self.package_reader=PackageReader(project_path)
        self.dependency_manager=DependencyManager(project_path, project_info,self.package_reader)

    def get_installed_dependencies(self,package_name):
        installed_packages=self.package_reader.read_installed_packages()
        if package_name not in installed_packages:
            raise PackageNotInstalledException()
        package_version=installed_packages[package_name]
        full_pkg_name=f"{package_name}-{package_version}"
        return self.dependency_manager.get_installed_package_dependencies(full_pkg_name)

    def get_dependencies_pypi(self,package_name):
        return self.dependency_manager.get_dependencies_pypi(package_name)

if __name__ == '__main__':
    project_path='C:/Users/vland/source/repos/depmanagertestproject'
    p_info=ProjectInfo()
    p=ProjectExplorer(project_path,p_info)
    dep=p.get_dependencies_pypi('pandas')
    f=p.dependency_manager.filter_by_installable(dep)
    print(f)