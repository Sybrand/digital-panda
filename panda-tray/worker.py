

class BaseWorker(object):
    def __init__(self):
        self._hadWorkToDo = False

    def _get_hadWorkToDo(self):
        return self._hadWorkToDo

    def _set_hadWorkToDo(self, value):
        self._hadWorkToDo = value

    hadWorkToDo = property(_get_hadWorkToDo)
