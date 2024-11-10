import os


class DependencyManager():
    def __init__(self, project_path):
        self.project_path = project_path

    def get_all_dependencies(self, package):
        pass

    def get_optional_dependencies(self, package):
        pass

    def get_required_dependencies(self, package):
        pass

    def read_metadata(self,package):
        metadata_path=os.path.join(self.project_path, 'venv', 'Lib', 'site-packages', )