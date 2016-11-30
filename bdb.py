from bdb.bdb import Bdb


# temporary ugliness
def init():
    global _db, add, log, info, history, edit, inv, stats
    global backup, restore, bulk_add
    _db = Bdb()
    add, log, info, history, edit, inv, stats = \
        _db.add, _db.log, _db.info, _db.history, _db.edit, _db.inv, _db.stats
    backup, restore, bulk_add = \
        _db.backup, _db.restore, _db.bulk_add

init()
