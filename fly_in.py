from parsing import ParsingError, Graph


def main():
    graph = Graph()
    for con in graph.connections:
        print(con.groupdict()["node1"])


if __name__ == "__main__":
    try:
        main()
    except ParsingError as e:
        print(e)
