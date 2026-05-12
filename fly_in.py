import re
import sys

if __name__ == "__main__":
    hub_regex = r"^hub:\s+.*\s-?\d+\s-?\d+\s\[(.*?)\]$"
    start_regex = r""
    finish_regex = r""
    drone_num_regex = r""
    connections_regex = r""
    hubs = []
    start = []
    finish = []
    drone_num = []
    connections = []

    for line in open(sys.argv[1], 'r'):
        if not len(line.strip()) or line.strip().startswith('#'):
            continue
        print(line)
        line.strip()
        if re.search(hub_regex, line):
            hubs.append(line)
        elif re.search(start_regex, line):
            start.append(line)
        elif re.search(finish_regex, line):
            finish.append(line)
        elif re.search(drone_num_regex, line):
            drone_num.append(line)
        elif re.search(connections_regex, line):
            connections.append(line)

    print(len(hubs))
    # print(start)
    # print(finish)
    # print(drone_num)
    # print(connections)
    #
    #
