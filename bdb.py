import shelve
from collections import namedtuple
import time
import json
from itertools import izip_longest


class Battery(object):

    def __init__(self, sn, manu=None, pn=None, entries=None):
        assert isinstance(sn, int)
        self.sn = sn
        self.manu = manu
        self.pn = pn
        self.entries = entries or []

    def __str__(self):
        string = "Battery(sn=%s" % self.sn
        if self.manu:
            string += ", manu=%s" % self.manu
        if self.pn:
            string += ", pn=%s" % self.pn
        if self.last_entry:
            string += ", last_entry=%s" % str(self.last_entry)
        string += ')'
        return string

    @property
    def last_entry(self):
        try:
            return self.entries[-1]
        except IndexError:
            return None

    def add_entry(self, entry):
        assert isinstance(entry, Entry)
        self.entries.append(entry)

    def last_known_values(self):
        # TODO: don't know if this is needed; may already be tracked 
        # due to how entries are created
        v = None
        mah = None
        status = None
        location = None
        for entry in self.entries:
            if entry.v:
                v = entry.v
            if entry.mah:
                mah = entry.mah
            if entry.status:
                status = entry.status
            if entry.location:
                location = entry.location
        return v, mah, status, location

    def to_dict(self):
        d = {
            'battery' : {
                'sn': self.sn,
                'manu': self.manu,
                'pn': self.pn,
                'entries': [entry.to_dict() for entry in self.entries],
                }
            }
        return d

    @classmethod
    def from_dict(cls, data):
        battery = data['battery']
        sn = int(battery['sn'])
        manu = battery['manu']
        pn = battery['pn']
        entries = []
        for raw_entry in battery['entries']:
            entry = Entry.from_dict(raw_entry)
            entries.append(entry)
        return cls(sn, manu, pn, entries)


class Entry(object):

    def __init__(
            self,
            v=None,
            mah=None,
            status=None,
            location=None,
            notes=None,
            ts=None):
        assert isinstance(ts, (float, None.__class__))
        assert isinstance(v, (int, float, None.__class__))
        assert isinstance(mah, (int, None.__class__))
        assert isinstance(notes, (str, None.__class__))
        if not any([v, mah, status, location, notes]):
            raise RuntimeError('Null entry')
        self.ts = ts or time.time()
        self.v = v
        self.mah = mah
        self.status = status
        self.location = location
        self.notes = notes

    @classmethod
    def from_previous(
            cls,
            entry,
            v=None,
            mah=None,
            status=None,
            location=None,
            notes=None):
        if not entry:
            return cls(v, mah, status, location, notes)
        new_status = status or entry.status
        new_location = location or entry.location
        new_v = v or entry.v
        new_mah = mah or entry.mah
        new_notes = notes or entry.notes
        return cls(new_v, new_mah, new_status, new_location, new_notes)

    @property
    def timestamp(self):
        return time.strftime('%y%m%d-%H%M%S', time.gmtime(self.ts))

    def __str__(self):
        string = "Entry(ts=%s" % self.timestamp
        if self.v:
            string += ", v=%s" % self.v
        if self.mah:
            string += ", mah=%s" % self.mah
        if self.status:
            string += ", status=%s" % self.status
        if self.location:
            string += ", location=%s" % self.location
        if self.notes:
            string += ", notes=%s" % self.notes
        string += ')'
        return string

    def to_dict(self):
        d = {
            'entry': {
                'ts': self.ts,
                'v': self.v,
                'mah': self.mah,
                'status': self.status,
                'location': self.location,
                'notes': self.notes,
                }
            }
        return d

    @classmethod
    def from_dict(cls, data):
        entry = data['entry']
        ts = float(entry.get('ts'))
        v = entry.get('v')
        mah = entry.get('mah')
        status = entry.get('status')
        location = entry.get('location')
        notes = entry.get('notes')
        return cls(v, mah, status, location, notes, ts)
        

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
        return self._db.get(Bdb.IDX_KEY)

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
            battery.add_entry(
                Entry(v, mah, status, location, notes)
            )
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
        if not v:
            v = []
        if not mah:
            mah = []
        if not status:
            status = []
        if not location:
            location = []
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
        entry = Entry.from_previous(
            battery.last_entry,
            v,
            mah,
            status,
            location,
            notes
        )
        battery.add_entry(entry)
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
            if battery.last_entry:
                if battery.last_entry.mah:
                    total_mah += battery.last_entry.mah
                    count_avg += 1
        print "Count: %d  Total Ah: %.2f  Avg mAh: %d" % (
            count, total_mah / 1000.0, total_mah / count_avg)
            

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
