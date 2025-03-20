import os
from pathlib import Path
import re


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

    @staticmethod
    def get_installed_version(pkg_name,project_path):
        site_packages_path = os.path.join(project_path, '.venv', 'Lib', 'site-packages')
        site_packages_contents = os.listdir(site_packages_path)
        for file in site_packages_contents:
            if file.endswith('.dist-info') or file.endswith('.egg-info'):
                package_and_version = Path(file).stem.split('-', 1)
                package = package_and_version[0]
                version = package_and_version[1]
                if package == pkg_name:
                    return version

    @staticmethod
    def get_version_reqs(dependency):
        #info=re.findall(r"(.*)(<=|>=|==|>|<)((\s*[\d\.]+\d(post|dev|pre)*)[0-9]*)",dependency)
        dependency = dependency.split(';')[0]
        #split the package name from its requirements
        info = re.findall(r"^[^<=|>=|==|>|<]*(<=|>=|==|>|<)(.*)$", dependency)
        info = [tuple(filter(None, item)) for item in info]
        results = [r.strip() for tup in info for r in tup]
        results = "".join(results)
        if len(results) == 0:
            #no requirements info was given, return the package name
            return dependency, None
        pkg_name = dependency.split(results[0])[0]
        if '(' in pkg_name:
            pkg_name = pkg_name.split('(')[0]
        pkg_name = pkg_name.strip()
        if ')' in results:
            results = results.split(')')[0]

        results=results.split(',')
        reqs={}
        for result in results:
            comp_and_version=re.findall(r"(<=|>=|==|>|<)(.*)",result)
            comp_and_version=[i for i in comp_and_version[0]]
            comp=comp_and_version[0]
            version=comp_and_version[1]
            reqs[comp]=version
        return pkg_name, reqs

    @staticmethod
    def get_package_name(dependency):
        dependency = dependency.split(';')[0]
        # split the package name from its requirements
        info = re.findall(r"^[^<=|>=|==|>|<]*(<=|>=|==|>|<)(.*)$", dependency)
        info = [tuple(filter(None, item)) for item in info]
        results = [r.strip() for tup in info for r in tup]
        results = "".join(results)
        if len(results) == 0:
            # no requirements info was given, return the package name
            return dependency, None
        pkg_name = dependency.split(results[0])[0]
        if '(' in pkg_name:
            pkg_name = pkg_name.split('(')[0]
        pkg_name = pkg_name.strip()
        return pkg_name

if __name__ == '__main__':
    project_path = 'C:/Users/vland/source/repos/depmanagertestproject'
    package_reader = PackageReader(project_path)
    print(package_reader.read_installed_packages())