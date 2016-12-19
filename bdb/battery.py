
from entry import Entry


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

    @property
    def v(self):
        if self.last_entry:
            return self.last_entry.v

    @property
    def mah(self):
        if self.last_entry:
            return self.last_entry.mah

    @property
    def status(self):
        if self.last_entry:
            return self.last_entry.status

    @property
    def location(self):
        if self.last_entry:
            return self.last_entry.location

    @property
    def notes(self):
        if self.last_entry:
            return self.last_entry.notes

    def add_entry(
            self,
            v=None,
            mah=None,
            status=None,
            location=None,
            notes=None,
            ts=None):
        self.entries.append(
            Entry.from_previous(
                self.last_entry,
                v,
                mah,
                status,
                location,
                notes
            )
        )

    def del_last_entry(self):
        self.entries = self.entries[:-1]

    def to_dict(self):
        d = {
            'battery': {
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
