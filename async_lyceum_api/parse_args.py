from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-w', '--web-host', default='0.0.0.0')
    parser.add_argument('-p', '--web-port', default=80, type=int)
    parser.add_argument('-H', '--postgres-host', default='0.0.0.0')
    parser.add_argument('-U', '--user', default='postgres')
    parser.add_argument('-D', '--database', default='db')
    parser.add_argument('-P', '--postgres-port', default=5432, type=int)
    parser.add_argument('-S', '--postgres-secret', required=False)

    return parser.parse_args()