from Command import Command
from DependencyManager import DependencyManager

class DependencyCommand(Command):
    def __init__(self,project_path,package_reader,project_info):
        Command.__init__(self,DependencyManager(project_path,package_reader,project_info))

    def run(self,args):
        if args.all:
