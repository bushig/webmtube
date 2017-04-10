import sys

from utils import before_shutdown_handler
from caching import del_all_cache


def main():
    if (len(sys.argv) == 2):
        arg = sys.argv[1]
        if arg == '-save':
            before_shutdown_handler()
        elif arg == '-flush':
            del_all_cache()
        else:
            print('Invalid  command')
    else:
        print(
            'usage: \n'
            '"python service.py -save" to save data in cache to DB\n'
            '"python service.py -flush" to delete all WEBM cache(not likes/views)')


if __name__ == "__main__":
    main()
