from parsing import ParsingError, Graph


def main():
    graph = Graph()
    print(graph.drone_num)
    print(graph.start)
    print(graph.hubs)
    print(graph.finish)
    print(graph.connections)


if __name__ == "__main__":
    try:
        main()
    except ParsingError as e:
        print(e)
