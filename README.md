# batterydb

## What is it

batterydb, or bdb, is a database for tracking battery inventories.  I'm developing it for my own project that will use an inventory of several thousand 18650 battery cells.

Add a cell to the database with an optional manufacturer and model number and you'll get a serial number to apply to the cell.  Using the cell serial number you can record various measurements, cell status, location, and notes, and track these over time.

## Example

Currently, bdb has no real interface.  Here is an example of how to use it.

    localhost:batterydb jmp$ python -i bdb.py
    >>> inv()
    Battery(sn=2, manu=samsung, pn=26c, last_entry=Entry(ts=161201-093322, v=4.15, mah=2200))
    Battery(sn=1, manu=sony, pn=18650se)
    >>> log(2,mah=2150)
    Battery(sn=2, manu=samsung, pn=26c, last_entry=Entry(ts=161201-093427, v=4.15, mah=2150))
    >>> history(2)
    Entry(ts=161201-093322, v=4.15, mah=2200)
    Entry(ts=161201-093427, v=4.15, mah=2150)
    Battery(sn=2, manu=samsung, pn=26c, last_entry=Entry(ts=161201-093427, v=4.15, mah=2150))
    >>> 
    jmp-mbp:batterydb jmp$ python -i bdb.py
    >>> add('samsung','28e')
    Battery(sn=3, manu=samsung, pn=28e)
    >>> log(3,v=3.86)
    Battery(sn=3, manu=samsung, pn=28e, last_entry=Entry(ts=161201-093526, v=3.86))
    >>> log(3,mah=2150)
    Battery(sn=3, manu=samsung, pn=28e, last_entry=Entry(ts=161201-093535, v=3.86, mah=2150))
    >>> history(3)
    Entry(ts=161201-093526, v=3.86)
    Entry(ts=161201-093535, v=3.86, mah=2150)
    Battery(sn=3, manu=samsung, pn=28e, last_entry=Entry(ts=161201-093535, v=3.86, mah=2150))
    >>> inv()
    Battery(sn=2, manu=samsung, pn=26c, last_entry=Entry(ts=161201-093427, v=4.15, mah=2150))
    Battery(sn=1, manu=sony, pn=18650se)
    Battery(sn=3, manu=samsung, pn=28e, last_entry=Entry(ts=161201-093535, v=3.86, mah=2150))
    >>> stats()
    Count: 3  Total Ah: 4.30  Avg mAh: 2150
    >>>

## Future

Eventually I want to be able to run queries to pull specific cells based on attributes such as manufacturer, model, capacity (mah), etc.  Also, I want to add functionality to build out battery packs to specific specifications from existing inventory.

## Fields

manu = text field to identify manufacturer
pn = text field to identify cell part number
sn = integer field for cell serial number
v = float field for voltage
mah = integer field to track mAh
status = text field for general use; I'm going to use it to track whether a cell is: storage, inuse, disposed, etc.
location = text field for general use; I'm going to use it to tracj whether a cell is in storage or in a specific pack.
notes = text field for general use
