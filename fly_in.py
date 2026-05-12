from parsing import ParsingError, Graph


def main():
    graph = Graph()
    print(graph.drone_num)
    print(graph.start.groupdict().get("meta_data"))
    for hub in graph.hubs:
        print(hub.groupdict().get("meta_data"))
    print(graph.finish)
    print(graph.connections)


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
