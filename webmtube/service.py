import sys

from webmtube.caching import del_all_cache
from webmtube.utils import before_shutdown_handler


def main():
    if (len(sys.argv) == 2):
        arg = sys.argv[1]
        if arg == '-save':
            before_shutdown_handler()
        elif arg == '-flush':
            del_all_cache()
        elif arg == '-celerypurge':
            from .tasks import app
            app.control.purge()
        else:
            print('Invalid  command')
    else:
        print(
            'usage: \n'
            '"python service.py -save" to save data in cache to DB\n'
            '"python service.py -flush" to delete all WEBM cache(not likes/views)\n'
            '"python service.py -celerypurge" to delete task queue\n'
        )


if __name__ == "__main__":
    main()
