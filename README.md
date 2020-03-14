### SAVE2VC

This is a script to migrate saves from GBA to the Wii U virtual console

**RESIZING EXPERIMENTAL, USE WITH CAUTION!**

Usage is as follows:

Extract a GBA save from a Wii U virtual console save:
```
python3 SAVE2VC.py extract data_008_0000.bin -o gba.sav
```

Inject a GBA save into a Wii U virtual console save:
```
python3 SAVE2VC.py inject data_008_0000.bin -s gba.sav -o modified.bin
```

```
usage: SAVE2VC.py [-h] [-s SAVE] [-o OFILE] [-e] [-r] {extract,inject} ifile

A script to migrate saves from GBA to Wii U VC

positional arguments:
  {extract,inject}      The command you want to use
  ifile                 The Wii U VC save file

optional arguments:
  -h, --help            show this help message and exit
  -s SAVE, --save SAVE  The save file to inject
  -o OFILE, --ofile OFILE
                        The file to output to
  -e, --eeprom          EEPROM byte swap
  -r, --resize          Attempt to resize the STATRAM0 block
```