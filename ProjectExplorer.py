from PackageReader import PackageReader


class ProjectExplorer():
    def __init__(self, project_path):
        self.project_path = project_path
        self.package_reader=PackageReader(project_path)

if __name__ == '__main__':
    p=ProjectExplorer('C:/Users/vland/source/repos/proiectcoo/')
    p.package_reader.read_packages()