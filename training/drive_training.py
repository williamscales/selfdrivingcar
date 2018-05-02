import sys

from sunfounder import app


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    app()

    return 0


if __name__ == '__main__':
    sys.exit(main())
