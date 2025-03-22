import os


class ProjectInfo():
    def get_python_version(self,project_path):
        cfg_path = os.path.join(project_path, '.venv', 'pyvenv.cfg')
        with open(cfg_path, 'r') as f:
            line=f.readline()
            while not line.startswith('version_info'):
                line=f.readline()
        return line.split('.final')[0].split(" = ")[1]

if __name__ == '__main__':
    project_info=ProjectInfo()
    print(project_info.get_python_version('C:/Users/vland/source/repos/depmanagertestproject'))