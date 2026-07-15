class DictExt(dict):
    def __getattr__(self, val):
        return self[val]
