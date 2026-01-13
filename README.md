# Program pro analýzu a interpretaci jednoduchého třídního čistě objektově orientovaného imperativního jazyka SOL25

Skript typu filtr (parse.py v jazyce Python 3.11) načte ze standardního vstupu zdrojový kód v SOL25
(viz sekce 3), zkontroluje lexikální, syntaktickou a statickou sémantickou správnost kódu a vypíše na
standardní výstup XML reprezentaci abstraktního syntaktického stromu programu dle specifikace
v sekci 4.1.


## Tento skript bude pracovat s těmito parametry:
• --help viz společný parametr všech skriptů v sekci 2.2.
Chybové návratové kódy specifické pro analyzátor:
• 21 - lexikální chyba ve zdrojovém kódu v SOL25;
• 22 - syntaktická chyba ve zdrojovém kódu v SOL25;
• 31 - sémantická chyba - chybějící třída Main či její instanční metoda run.
• 32 - sémantická chyba - použití nedefinované (a tedy i neinicializované) proměnné, formálního
parametru, třídy, nebo třídní metody.
• 33 - sémantická chyba arity (špatná arita bloku přiřazeného k selektoru při definici instanční
metody)
• 34 - sémantická chyba - kolizní proměnná (lokální proměnná koliduje s formálním parametrem
bloku);
• 35 - sémantická chyba - ostatní.


Příklad úryvku jazyka SOL25:
```
[ :one :two | r := Integer from: two. ]
```

a jemu odpovídající XML:
```xml
<block arity="2">
    <parameter name="one" order="1" />
    <parameter name="two" order="2"></parameter >
    <assign order="1">
    <var name="r"/>
        <expr>
            <send selector="from:">
                <expr><literal class="class" value="Integer" /></expr>
                <arg order="1">
                    <expr><var name="two" /></expr>
                </arg>
            </send>
        </expr>
    </assign>
</block>
```