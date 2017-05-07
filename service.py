import sys

from webmtube.app import get_app
from webmtube.caching import del_all_dirty_cache, del_all_clean_cache
from webmtube.utils import before_shutdown_handler


def main():
    if (len(sys.argv) == 2):
        arg = sys.argv[1]
        if arg == '-save':
            get_app()  # Have to init DB
            before_shutdown_handler()
        elif arg == '-flush':
            del_all_dirty_cache()
        elif arg == '-flushclean':
            del_all_clean_cache()
        elif arg == '-celerypurge':
            from webmtube.tasks import app
            app.control.purge()
        else:
            print('Invalid  command')
    else:
        print(
            'usage: \n'
            '"python service.py -save" to save data in cache to DB\n'
            '"python service.py -flush" to delete dirty WEBM cache(not likes/views)\n'
            '"python service.py -flushclean" to delete clean WEBM cache(not likes/views)\n'
            '"python service.py -celerypurge" to delete task queue\n'
        )


if __name__ == "__main__":
    main()
