Implementační dokumentace k 1. úloze do IPP 2020/2021
Jméno a příjmení: Kateřina Cibulcová
Login: xcibul12

## Analyzátor kódu v IPPcode21 (parse.php)

### Parametry skriptu

Skript se spouští skrze příkazovou řádku bez parametrů nebo s parametrem --help, který vytiskne nápovědu ke skriptu.

### Zpracování programu v jazyce IPPcode21

Pomocí smyčky while je čten stardardní vstup řádek po řádku. Nejdříve je zkontrolována hlavička programu a poté co je přečtena hlavička jsou jednotlivé řádky programu rozděleny funkcí preg_split(). Řádek je rozdělen bílými znaky a tyto částy jsou uloženy do pole instructionParts. Pomocí tohoto pole jsou využívány jednotlivé operandy instrukcí a také operační kód. Podle operačního kódu instrukce je s pomocí řídicí struktury switch určen povolený počet operandů a typ operandů. 

Následně je použita funkce argParser(), která zpracovává operandy instrukce. Funkce pracuje tak, že očekává jako parametry konkrétní hodnotu operandu, pořadí operandu, typ operandu a XML element instrukce. Operandy jsou potom přiřazeny jako atributy elementu konkrétní instrukce. 

### Generování XML reprezentace programu

Po zpracování progamu a vytvoření XML reprezentace je XML generováno na standardní výstup.
Pro generování XML kódu je použita XML DOM built-in knihovna jazyka PHP.

