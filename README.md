# lmtools

A python package and collection of scripts, allowing currently connected mbed boards to be listed.

Usage
```
$ lm.py
+----------+-------+-------+--------------------------------------+
| Name     |  Port | Drive | Serial Number                        |
+----------+-------+-------+--------------------------------------+
| LPC1549  | COM16 |   G   | 15490200055870CBF8A79A7A             |
| NRF51822 | COM15 |   F   | 107002001FE6E019E2190F91             |
| LPC1768  |  COM6 |   E   | 10109F5C1C9AB51462E9D8C8AFF6DFA2DCDC |
+----------+-------+-------+--------------------------------------+
```

It is currently only compatible with Windows, however Linux support is fairly trivial to add, and folders have already been added to lmtools in expectation of this.

```
lmgui.pyw
```

This produces a small widget in the top left hand corner of the screen showing currently connected mbed devices, their drive letter and com port. Again this only works for Windows currently.