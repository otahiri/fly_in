import sys
from parsing import ParsingError, Graph


def main():
    lines = list()
    with open(sys.argv[1], "r") as map:
        lines = [
            line.strip("\n")
            for line in map
            if len(line.strip()) and not line.strip().startswith("#")
        ]
    graph = Graph(lines)
    print(graph.drone_num)


if __name__ == "__main__":
    try:
        main()
    except (
        ParsingError,
        IsADirectoryError,
        PermissionError,
        FileNotFoundError,
    ) as e:
        print(e)
