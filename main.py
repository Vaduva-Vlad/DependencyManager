import argparse
from commands.VulnerabilityCommand import VulnerabilityCommand


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Diagnose issues with dependencies")
    parser.add_argument("--vuln",action="store_true")
    parser.add_argument("--pkg_vuln")
    args=parser.parse_args()

    command=VulnerabilityCommand("C:/Users/vland/source/repos/depmanagertestproject")
    command.run(args)