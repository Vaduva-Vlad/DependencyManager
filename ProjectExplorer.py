import argparse

from ProjectInfo import ProjectInfo
from commands.VulnerabilityCommand import VulnerabilityCommand
from exceptions.PackageNotInstalledException import PackageNotInstalledException

from DependencyManager import DependencyManager
from PackageReader import PackageReader
from security.VulnerabilityChecker import VulnerabilityChecker


class ProjectExplorer:
    def __init__(self, project_path,project_info):
        self.project_path = project_path
        self.project_info = project_info
        self.package_reader=PackageReader(project_path)
        self.dependency_manager=DependencyManager(project_path, project_info,self.package_reader)
        self.vulnerability_checker=VulnerabilityChecker(project_path)

    def get_installed_dependencies(self,package_name):
        installed_packages=self.package_reader.read_installed_packages()
        if package_name not in installed_packages:
            raise PackageNotInstalledException()
        package_version=installed_packages[package_name]
        full_pkg_name=f"{package_name}-{package_version}"
        return self.dependency_manager.get_installed_package_dependencies(full_pkg_name)

    def get_dependencies_pypi(self,package_name):
        return self.dependency_manager.get_dependencies_pypi(package_name)

    def run_command(self,args):
        if args.vuln or args.pkg_vuln:
            command = VulnerabilityCommand(self.project_path)
            command.run(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Diagnose issues with dependencies")
    parser.add_argument("--vuln", action="store_true")
    parser.add_argument("--pkg_vuln")
    parser.add_argument("--scan-dependencies",choices=["all","circular","versions"])
    args = parser.parse_args()
    project_path=''
    p_info=ProjectInfo()
    p=ProjectExplorer(project_path,p_info)

    p.run_command(args)