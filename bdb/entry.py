import time


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
