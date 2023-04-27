# IPP
Univerzitní projekt pro předmět IPP (Principy programovacích jazyků - Principles of programming languagues)

# Část 1 - Analyzátor kódu v jazyce IPP-code21
Skript typu filtr (parse.php v jazyce PHP 7.4) načte ze standardního vstupu zdrojový kód v IPP-
code21, zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardní
výstup XML reprezentaci programu.

# Část 2 - Interpret XML reprezentace kódu

Skript (interpret.py v jazyce Python 3.8) načte XML reprezentaci programu a tento program
s využitím vstupu dle parametrů příkazové řádky interpretuje a generuje výstup. Vstupní XML
reprezentace je např. generována skriptem parse.php ze zdrojového kódu v IPPcode21.
