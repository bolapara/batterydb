import shelve
import json
from itertools import izip_longest

from battery import Battery


class Bdb(object):
    IDX_KEY = '__index'

    def __init__(self, fn='b.db'):
        self._db = shelve.open(fn)

    def _serialize(self):
        return json.dumps(
            [battery.to_dict() for battery in self._get_all_batteries()]
        )

    def _deserialize(self, data):
        battery_list = json.loads(data)
        for battery_raw in battery_list:
            battery = Battery.from_dict(battery_raw)
            self._put(battery, overwrite=True)

    def backup(self, filename):
        with open(filename, 'w') as fobj:
            fobj.write(self._serialize())

    def restore(self, filename):
        with open(filename, 'r') as fobj:
            self._deserialize(fobj.read())

    @property
    def _index(self):
        return self._db.get(Bdb.IDX_KEY, 0)

    @_index.setter
    def _index(self, index):
        assert isinstance(index, int)
        if index > self._index:
            self._db[Bdb.IDX_KEY] = index

    def _exists(self, sn):
        if str(sn) in self._db:
            return True
        return False

    def _get(self, sn):
        if not self._exists(sn):
            raise RuntimeError('sn %d does not exist' % sn)
        return self._db.get(str(sn))

    def _get_all_batteries(self):
        for battery in self._db.values():
            if isinstance(battery, Battery):
                yield battery

    def _put(self, battery, overwrite=False):
        if not overwrite:
            if self._exists(battery.sn):
                raise RuntimeError('sn %d already exists' % battery.sn)
        self._db[str(battery.sn)] = battery
        self._index = battery.sn

    def add(self,
            manu=None,
            pn=None,
            v=None,
            mah=None,
            status=None,
            location=None,
            notes=None,
            sn=None):
        sn = sn or self._index + 1
        battery = Battery(sn, manu, pn)
        if any([v, mah, status, location, notes]):
            battery.add_entry(v, mah, status, location, notes)
        self._put(battery)
        print battery

    def bulk_add(
            self,
            manu=None,
            pn=None,
            v=None,
            mah=None,
            status=None,
            location=None,
            count=0):
        v = v or []
        mah = mah or []
        status = status or []
        location = location or []
        for entry_params in izip_longest(
                v,
                mah,
                status,
                location,
                range(count),
                fillvalue=None):
            self.add(
                manu,
                pn,
                v=entry_params[0],
                mah=entry_params[1],
                status=entry_params[2],
                location=entry_params[3]
            )

    def log(self, sn, v=None, mah=None, status=None, location=None, notes=None):
        if not any([v, mah, status, location, notes]):
            raise RuntimeError('Nothing to log')
        battery = self._get(sn)
        battery.add_entry(v, mah, status, location, notes)
        self._put(battery, overwrite=True)
        print battery

    def info(self, sn):
        battery = self._get(sn)
        print battery

    def history(self, sn):
        battery = self._get(sn)
        for entry in battery.entries:
            print entry
        print battery

    def edit(self, sn, manu=None, pn=None):
        battery = self._get(sn)
        battery.manu = manu or battery.manu
        battery.pn = pn or battery.pn
        self._put(battery, overwrite=True)

    def delete(self, sn):
        del self._db[str(sn)]

    def inv(self):
        for battery in self._get_all_batteries():
            print battery

    def stats(self):
        total_mah = 0
        count = 0
        count_avg = 0
        for battery in self._get_all_batteries():
            count += 1
            if battery.mah:
                total_mah += battery.mah
                count_avg += 1
        print "Count: %d  Total Ah: %.2f  Avg mAh: %d" % (
            count, total_mah / 1000.0, total_mah / count_avg)

    def dist(self):
        distdict = {}
        for battery in self._get_all_batteries():
            mah = battery.mah
            if mah:
                ah = round(mah / 1000.0, 1)
                cur = distdict.get(ah, 0)
                cur += ah
                distdict[ah] = round(cur, 1)
        for key in sorted(distdict.keys()):
            val = distdict[key]
            print '%.1f: %4d (%.1f)' % (key, int(val/key), val)
