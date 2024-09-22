#
# An observable list for managing selection state amongst the various windows.
#
# TODO reconcile: ViewOne does selection by imgname and pyphoto.canvas by btn
#
class ObservableList:
    def __init__(self):
        self._observers = []
        self._items = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def _notify_observers(self, action, item):
        for observer in self._observers:
            observer.observe_update(action, item)

    def get_items(self):
        return self._items
        
    def clear(self):
      # clear the list
        self._notify_observers('clear', self._items)
        self._items = []
        
    def set(self, value):
      # set the list to a new item
        if len(self._items) != 0:
          self.clear()       # let everyone see the old list first
        self._items.append(value)
        self._notify_observers('set', self._items)

    def extend(self, item):
      # add a single item to the list
        self._items.append(item)
        self._notify_observers('extend', self._items)

    def toggle(self, item):
      # a single item, add if not in the list, remove otherwise
      if item in self._items:
        self._notify_observers('clear', self._items)
        self._items.remove(item)
      else:
        self._items.append(item)
      self._notify_observers('set', self._items)
      
    def setList(self, inlist):
      # set the list to a new LIST of values (notify everyone once)
      self.clear()
      for item in inlist:
        self._items.append(item)
      self._notify_observers('set', self._items)
      
    def setByName(self, value):
      # selection change by filename, not btn
        if len(self._items) != 0:
          self.clear()       # let everyone see the old list first
        self._items.append(value)
        self._notify_observers('set', self._items)
      
