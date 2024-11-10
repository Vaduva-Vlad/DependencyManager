class PackageNotInstalledException(Exception):
    def __init__(self):
        super().__init__("The specified package is not installed in the repository.")
