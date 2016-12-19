from bdb.bdb import Bdb


# temporary ugliness
_db = Bdb()
for attr in dir(_db):
    if callable(getattr(_db, attr)):
        if not attr.startswith('_'):
            exec('%s = _db.%s' % (attr, attr))
