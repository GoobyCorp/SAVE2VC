### GBA2WIIU

This is a script to migrate saves from GBA to the Wii U virtual console

Usage is as follows:
```
usage: GBA2WIIU.py [-h] [-s SAVE] [-o OFILE] [-e] [-r] {extract,inject} ifile

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
  -r, --resize          Attempt to resize the save STATRAM0 block
```