#!/usr/bin/env python3

import subprocess
import sys
import apt
import apt_pkg
from termcolor import colored, cprint

PACKAGE_MANAGER = 'nala' # replace this with apt if you don't use nala'

# Define the APT search command to use
# TODO: replace with apt_pkg equivelent
SEARCH_COMMAND = ['apt-cache', 'search']
apt_pkg.init()
cache = apt_pkg.Cache()

def search_packages(search_term):
    search_term = search_term.split(' ')
    command = SEARCH_COMMAND + search_term
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8')


def parse_packages(search_result):
    packages = []
    for line in search_result.split('\n'):
        if not line:
            continue
        parts = line.split(' ', 1)
        if len(parts) != 2:
            continue
        package = parts[0]
        description = parts[1]
        packages.append((package, description))
    return packages

# Display a list of packages and prompt the user to select packages
def select_packages(packages):
    if not packages:
        print('No packages found.')
        return []

    # Reverse the order of the packages because they tend to be shown in the wrong order
    packages.reverse()

    print('Select packages (separated by spaces):')
    for i, package in enumerate(packages):
        status = ''

        # Get current version and install state
        try:
            version = cache[package[0]].version_list[0].ver_str
            if cache[package[0]].current_state == apt_pkg.CURSTATE_INSTALLED:
                status = '[installed]'
                if version != cache[package[0]].current_ver.ver_str:
                    status = '[installed: ' + cache[package[0]].current_ver.ver_str + ']'
            else:
                    status = ''
        except:
            # Hacky alternative solution that seems to work when the other doesn't. Much slower and less secure so shouldn't be used first.
            version = subprocess.check_output(['apt-cache', 'show', package[0]]).decode('utf-8').strip().split('\n')
            version = next((line for line in version if line.startswith('Version: ')), '')
            version = version[len('Version: '):].strip()
        cprint(f'{len(packages)-i}. ', "yellow", end='')     
        cprint(f'{package[0]} - ', "blue", end='')
        cprint(f'({version}) ', "yellow", end='')
        cprint(f'{package[1]} ', "green", end='')
        cprint(f'{status} ', "red")

    selected = input('> ').strip()
    selected_indices = []
    for index in selected.split(' '):
        try:
            selected_indices.append(len(packages) - int(index))
        except ValueError:
            pass

    return [packages[i][0] for i in selected_indices]


def main():
    if len(sys.argv) < 2:
        print('Usage: nay.py <search term>')
        sys.exit(1)
    search_term = ''
    for i in range(1,len(sys.argv)):
         search_term += sys.argv[i] + " "
    search_result = search_packages(search_term)
    packages = parse_packages(search_result)
    selected_packages = select_packages(packages)

    print(f'Selected packages: {", ".join(selected_packages)}')
    if selected_packages:
        command = ['sudo', PACKAGE_MANAGER, 'install'] + selected_packages
        subprocess.run(command)

    return selected_packages

if __name__ == '__main__':
    main()
