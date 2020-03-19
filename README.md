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
python3 SAVE2VC.py inject gba.sav data_008_0000.bin -o modified.bin
```
**Main:**
```
usage: SAVE2VC.py [-h] {extract,inject} ...

A script to migrate saves from GBA to Wii U VC

optional arguments:
  -h, --help        show this help message and exit

commands:
  {extract,inject}  Command help
    extract         Extract a game save from a Wii U VC save
    inject          Inject a game save into a Wii U VC save
```
**Extract:**
```
usage: SAVE2VC.py extract [-h] [-o OFILE] [-e] ifile

positional arguments:
  ifile                 The Wii U VC save file

optional arguments:
  -h, --help            show this help message and exit
  -o OFILE, --ofile OFILE
                        The file to output to
  -e, --eeprom          EEPROM byte swap
```
**Inject:**
```
usage: SAVE2VC.py inject [-h] [-o OFILE] [-e] [-r] sfile ifile

positional arguments:
  sfile                 The game save to inject
  ifile                 The Wii U VC save file

optional arguments:
  -h, --help            show this help message and exit
  -o OFILE, --ofile OFILE
                        The file to output to
  -e, --eeprom          EEPROM byte swap
  -r, --resize          Attempt to resize the STATRAM0 block
```