import sys
import json
import re
import subprocess 
import argparse
import pathlib

from dataclasses import dataclass

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

@dataclass
class Host:
    host: str = "" 
    hostname: str = "localhost"
    port: int = "22"
    user: str = "root"
    
    def to_ansible_dict(self) -> dict:
        return { 
                self.hostname: { 
                                "ansible_host": self.host, 
                                "ansible_port": self.port, 
                                "ansible_user": self.user 
                                }
                }

class InventoryGenerator:
    def initiate_parser():
        parser = argparse.ArgumentParser(
                prog="Ansible Inventory Generator",
                description="Generates Ansible Inventory",
                )

        parser.add_argument(
                "-d", "--destination",
                type=pathlib.Path,
                default="./"
                )

        parser.add_argument(
                "-f", "--format",
                choices=[
                    "json", 
                    #"ini" # TODO: Add support for INI format
                    #"yaml" # TODO: Add support for Yaml format
                    ],
                type=ascii,
                default="json"
                )

        parser.add_argument(
                "-r", "--role",
                type=ascii,
                required=True,
                nargs="*" # 0 or more, because we might have `ungrouped` hosts
                )

        return parser

    def reachable(host: str) -> bool:
        command = ['ping', '-c', '1', host]
        return subprocess.call(command) == 0

    def input_bool(prompt: str, default: bool) -> bool:
        while (True):
            abort = input(prompt)
            match (abort.lower()):
                case "yes" | "y" | "1": return True
                case "no" | "n" | "0": return False
                case "": return default

    def input_int(prompt: str, default: int) -> int:
        while (True):
            value = input(prompt)
         
            if (value == ""): 
                return default
    
            try:
                value = int(value)
                return value
            except ValueError:
                continue

    def input_hostname(prompt: str, default: str) -> str:
        pattern = r"(?!-)[a-z0-9-]{1,63}(?<!-)$"
        while (True):
            value = input(prompt)
            if (value == ""):
                print("hostname: returning default")
                return default
            if len(value) > 253:
                eprint(f"Provided hostname \"{value}\" is NOT valid - Too long.")
                continue
            if re.fullmatch(pattern, value) == None:
                eprint(f"Provided hostname \"{value}\" is NOT valid - You probably used invalid format or prohibited characters.")
                continue
            return value

    def input_user(prompt: str, default: str) -> str:
    
        pattern = "^[a-z][-a-z0-9_]*$" 
    
        while (True):
            value = input(prompt)
            if value == "":
                return default
            if re.fullmatch(pattern, value) == None:
                eprint(f"Provided username \"{value}\" is NOT valid - it does not follow NAME_REGEX=\"{pattern}\".")
                continue
            return value 

    def generate(host: Host):
        try:
            with open("inventory/hosts.json", "w") as file:
                inventory = { "openfire_server": { "hosts": host.to_ansible_dict() } }
                json.dump(inventory, fp=file, ensure_ascii=True, indent=2)
        except FileNotFoundError:
            eprint()
            eprint("ERROR: No such file or directory: \'inventory/hosts.json\'")
            eprint("Probably you tried to run the script not from the project's root directory.")
            eprint("Try to run next commands:")
            eprint()
            eprint("$ cd ..")
            eprint("$ task generate-inventory # Requires `task` to be installed.")
            eprint()
            eprint("or")
            eprint()
            eprint("$ cd ..")
            eprint("$ python3 scripts/generate-inventory.py")
            exit(0)

if __name__ == "__main__":
    print("############################################################")
    print("Welcome to an inventory generator.")
    print("You will need to provide host information.")
    print("############################################################")

    host_host = input("domain name/ip address: ")
    
    if not reachable(host_host):
        eprint(f"Provided host \"{host_host}\" is unreachable.")
        if not input_bool("Proceed? [y/N]: ", False):
            eprint("Aborting.")
            exit(1)

    host_hostname = input_hostname("hostname (default: localhost): ", "localhost")

    while (True):
        host_port = input_int("ssh port (default: 22): ", 22)
        if host_port < 1 or host_port > 65535:
            eprint(f"Provided port \"{value}\" is out of booundaries. Allowed ports are 0 to 65535.")
            continue
        break

    host_user = input_user("user (default: root): ", "root")

    host = Host(host=host_host, hostname=host_hostname, port=host_port, user=host_user)

    ########

    generator = InventoryGenerator()
    parser = generator.initiate_parser()
    args = parser.parse_args()

    generator.generate(args)
