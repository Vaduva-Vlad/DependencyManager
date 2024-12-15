import os
from pathlib import Path


class PackageReader():
    def __init__(self, project_path):
        self.project_path = project_path

    def read_installed_packages(self):
        package_info = {}
        site_packages_path = os.path.join(self.project_path, '.venv', 'Lib', 'site-packages')
        site_packages_contents = os.listdir(site_packages_path)
        always_installed_packages=['pip','setuptools','wheel']
        for file in site_packages_contents:
            if file.endswith('.dist-info') or file.endswith('.egg-info'):
                package_and_version = Path(file).stem.rsplit('-', 1)
                package = package_and_version[0]
                version = package_and_version[1]
                if package not in always_installed_packages:
                    package_info[package] = version
        return package_info

if __name__ == '__main__':
    project_path = 'C:/Users/vland/source/repos/depmanagertestproject'
    package_reader = PackageReader(project_path)
    print(package_reader.read_installed_packages())