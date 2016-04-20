from os.path import abspath, dirname, join

c = get_config()  # noqa
c.NotebookApp.extra_nbextensions_path = [
    join(dirname(abspath(__file__)), 'nbextensions'),
]
