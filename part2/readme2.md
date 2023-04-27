

Tato dokumentace popisuje implementační detaily skriptu `interpret.py`, který načítá 
a interpretuje XML reprezentaci kódu a následně kód provádí.

### Skript interpret.py

Implementace interpretu se skládá ze tří hlavních částí: hlavní funkce celého programu
(`main()`), kde se volá funkce pro zpracování argumentů programu (pro tento účel je
použit přístup k argumentům příkazové řádky skrz knihovnu `sys` ) a poté se čtou 
a ukládají data z XML reprezentace kódu za pomocí knihovny `ElementTree`, přičemž
se kontroluje jeho validita. V této hlavní funkci se volá také funkce
`execute(instructions)`, která očekává jako vstup právě uložená data z XML souboru
v podobě slovníku instrukcí seřazených podle pořadí instrukce (`order`). Z tohoto
slovníku jsou poté získávána data (operační kódy instrukcí a jejich argumenty).
Ve funkci `execute(instructions)` se nachází cyklus, který prochází instrukce podle 
pořadí instrukce (`order`) a je zároveň využitý i jako interní čítač instrukcí, 
což byl patrně největší problém celého programu, protože bylo nutné například
vyřešit i situaci, kdy jsou skokové instrukce rozmístěny v různém pořadí. 
Ve zmíněném cyklu je implementována důležitá řídící konstrukce interpretu, kde jsou 
podle operačních kódů volány příslušné metody z třídy pojmenované `Instruction`, 
která je třetí hlavní část programu. Tyto metody očekávají jako jeden z parametrů 
argumenty příslušné instrukce načtené knihovnou `ElementTree`. Případně jsou také 
některé instrukce (např. `EXIT` ) vykonávány přímo ve výše jmenované řídící konstrukci.

### Další implementační detaily skriptu

Důležitou částí interpretu byla také práce s regulárními výrazy, pro kterou je využívána knihovna `re` a jejich prostřednictvím je kontrolována správná struktura XML kódu – validní názvy proměnných, validní hodnoty určitých datových typů apod. V této části bylo zapotřebí důsledné ošetřování regulárních výrazů, což zabralo významné množství času strávené na projektu. Výše popsaným způsobem byly kontrolovány a ukládány argumenty instrukcí a tyto argumenty byly ještě jednou zpracovány jako operandy podle toho, zda šlo o instrukci se dvěma nebo třemi operandy.
Tyto argumenty poté byly seřazeny do polí a k určitým hodnotám je přistupováno skrz příslušné indexy. Tříd je využíváno zejména kvůli přehlednosti také v případě zásobníkových instrukcí (`Stack` ) a načtení všech návěští ze seznamu instrukcí (`Label`) a pro chybové hlášky a návratové kódy (`Error`).

