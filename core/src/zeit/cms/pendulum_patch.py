def reduce_without_nocache(self):
    # Simplified version of zoneinfo.ZoneInfo.__reduce__
    return (self.__class__, (self.key,))
