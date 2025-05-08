import argparse
from commands.VulnerabilityCommand import VulnerabilityCommand

def main():
    if args.vuln or args.pkg_vuln:
        command = VulnerabilityCommand("")
        command.run(args)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Diagnose issues with dependencies")
    parser.add_argument("--vuln",action="store_true")
    parser.add_argument("--pkg_vuln")
    args=parser.parse_args()

    main()