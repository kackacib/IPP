<?php
/* Fakulta informačních technologií VUT
 * IPP Projekt - 1. část: Analyzátor kódu v IPPcode21 (parse.php)
 * Autor: Kateřina Cibulcová (xcibul12)
 * Letní semestr 2020/2021
 */


ini_set('display_errors', 'stderr');

//Vytvoření XML objektu
$dom = new DOMDocument('1.0', 'UTF-8');
$dom->preserveWhiteSpace = false;
$dom->formatOutput = true;


//Chybové návratové kódy

abstract class Errors
{
    const ERROR_WRONG_ARGUMENTS = 10;
    const ERROR_WRONG_HEADER = 21;
    const ERROR_WRONG_OPCODE = 22;
    const ERROR_LEXICAL_ERROR = 23;
}

//--------->Spouštění programu<----------//


if (($argc == 2)) {

    if (($argv[1]) == ("--help") || ($argv[1] == ("-h"))) {
        echo("Tento skript slouzi jako analyzator kodu v jazyce IPPcode21.\nAnalyzator kodu nacita zdrojovy kod napsany v IPPcode21 ze standardniho vstupu,\nzkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni vystup XML reprezentaci programu.\nSkript se spousti ve tvaru: php parse.php <input_file\n");
        exit(0);
    } else {
        fwrite(STDERR, "Chybne argumenty programu! \n");
        exit(Errors::ERROR_WRONG_ARGUMENTS);
    }
}

//--------->Funkce pro zpracování operandů instrukcí<----------//

function argParser($symb, $argName, $type, $instruction)
{
    global $dom;
    $arg = $dom->createElement($argName);
    $frames = array("LF", "TF", "GF");
    $types = array("int", "bool", "string", "nil");
    $boolValues = array("true", "false");

    //Kontrola hodnot operandů podle typu instrukce
    if ($type == "type") {
        if (in_array($symb, ["int", "bool", "string"])) {
            if (strpos($symb, "@") != false) {
                fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                exit(Errors::ERROR_LEXICAL_ERROR);
            }
            $arg->setAttribute("type", "type");
            $type = $dom->createTextNode($symb);
            $arg = $instruction->appendChild($arg);
            $arg->appendChild($type);
            return;
        } else {
            echo "Chybna syntaxe instrukci zdrojoveho kodu!\n";
            exit(Errors::ERROR_LEXICAL_ERROR);
        }
    } elseif ($type == "label") {
        if (strpos($symb, "@") != false) {
            fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
            exit(Errors::ERROR_LEXICAL_ERROR);
        }
        if (preg_match('/[a-zA-Z_\-$&%*!?]+/', $symb[0])) {
            if (!preg_match('/[\w\-$&%*!?]*/', $symb)) {
                fwrite(STDERR,"Chybne pojmenovani navesti! Nazev musi obsahovat pouze alfanumericke znaky nebo uvedene specialnich znaku: _-$&%*!?\n");
                exit(Errors::ERROR_LEXICAL_ERROR);
            }
        } else {
            fwrite(STDERR,"Chybne pojmenovani navesti! Nazev musi zacinat pismenem nebo jednim z uvedenych specialnich znaku: _-$&%*!?\n");
            exit(Errors::ERROR_LEXICAL_ERROR);
        }
        $arg->setAttribute("type", "label");
        $label = $dom->createTextNode($symb);
        $arg = $instruction->appendChild($arg);
        $arg->appendChild($label);
        return;
    } else {
        //Pokud se jedná o proměnnou či konstantu, zkontrolujeme syntaxi a rozdělíme operand na datový typ a hodnotu
        if (strpos($symb, "@") == false) {
            fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
            exit(Errors::ERROR_LEXICAL_ERROR);
        }
        $symbParts = explode("@", $symb, 2);
        $dataType = $symbParts[0];
        $value = $symbParts[1];

        if ($type == "var") {
            if (in_array($dataType, $frames)) {
                if (preg_match('/[a-zA-Z_\-$&%*!?]+/', $value[0])) {
                    if (!preg_match('/[\w\-$&%*!?]*/', $value)) {
                        fwrite(STDERR, "Chybne pojmenovani promenne! Nazev musi obsahovat pouze alfanumericke znaky nebo uvedene specialnich znaku: _-$&%*!?\n");
                        exit(Errors::ERROR_LEXICAL_ERROR);
                    }
                } else {
                    fwrite(STDERR, "Chybne pojmenovani promenne! Nazev musi zacinat pismenem nebo jednim z uvedenych specialnich znaku: _-$&%*!?\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                $arg->setAttribute("type", "var");
                $var = $dom->createTextNode($symb);
                $arg = $instruction->appendChild($arg);
                $arg->appendChild($var);
            } else {
                fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                exit(Errors::ERROR_LEXICAL_ERROR);
            }
        } elseif ($type == NULL) {
            if (in_array($dataType, $frames)) {
                if (preg_match('/[a-zA-Z_\-$&%*!?]+/', $value[0])) {
                    if (!preg_match('/[\w\-$&%*!?]*/', $value)) {
                        fwrite(STDERR, "Chybne pojmenovani promenne! Nazev musi obsahovat pouze alfanumericke znaky nebo uvedene specialnich znaku: _-$&%*!?\n");
                        exit(Errors::ERROR_LEXICAL_ERROR);
                    }
                } else {
                    fwrite(STDERR, "Chybne pojmenovani promenne! Nazev musi zacinat pismenem nebo jednim z uvedenych specialnich znaku: _-$&%*!?\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                $arg->setAttribute("type", "var");
                $var = $dom->createTextNode($symb);
                $arg = $instruction->appendChild($arg);
                $arg->appendChild($var);
            } elseif(in_array($dataType, $types)) {

                if ($dataType == "bool") {
                    if (!in_array($value, $boolValues)) {
                        fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                        exit(Errors::ERROR_LEXICAL_ERROR);
                    }
                } else if ($dataType == "nil") {
                    if ($value != "nil") {
                        fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                        exit(Errors::ERROR_LEXICAL_ERROR);
                    }
                } else if ($dataType == "string") {
                    if (preg_match('/[\\\]+/', $value)) {
                        if (!preg_match('/(\\\\\d\d\d)+/', $value)) {
                            fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                            exit(Errors::ERROR_LEXICAL_ERROR);
                        }
                    }
                } else if ($dataType == "int") {
                    if (!preg_match('/^[-+]*[\d]+$/', $value)) {
                        fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                        exit(Errors::ERROR_LEXICAL_ERROR);
                    }
                }

                $arg->setAttribute("type", $dataType);
                $symbValue = $dom->createTextNode($value);
                $arg = $instruction->appendChild($arg);
                $arg->appendChild($symbValue);
            } else {
                fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                exit(Errors::ERROR_LEXICAL_ERROR);
            }
        }

    }

}

//--------->Procházení řádků programu IPPcode21<----------//

$headerChecked = false;
$order = 0;
while ($line = fgets(STDIN)) {

    //Odstranění komentáře
    if (strpos($line, "#") !== false) {
        $newLine = explode("#", $line, 2);
        $line = $newLine[0];
    }

    //Kontrola hlavičky
    if ($headerChecked == false) {
        if (strtoupper(trim($line)) == ".IPPCODE21") {
            $root = $dom->createElement("program");
            $root->setAttribute("language", "IPPcode21");
            $root = $dom->appendChild($root);

            $headerChecked = true;
            continue;
        } elseif (trim($line) == "") {
            continue;
        } else {
            fwrite(STDERR, "Chybna nebo chybejici hlavicka zdrojoveho kodu!\n");
            exit(Errors::ERROR_WRONG_HEADER);
        }
    }

        //Rozdělení instrukce na jednotlivé části
        $instructionParts = preg_split('/\s+/', trim($line));
        $opcode = $instructionParts[0];
        if ($opcode == "") {
            continue;
        }

        //Pořadí instrukce
        $order++;

        //Vytváření XML elementů pro následné generování
        $instruction = $dom->createElement("instruction");
        $instruction->setAttribute("order", $order);
        $instruction->setAttribute("opcode", strtoupper($opcode));
        $instruction = $root->appendChild($instruction);

        //Čtení a kontrola jednotlivých instrukcí
        switch (strtoupper($opcode)) {

            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK";
                if (count($instructionParts) > 1) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                break;
            case "LABEL":
            case "CALL":
            case "JUMP":
                if (count($instructionParts) != 2) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "label", $instruction);
                break;
            case "POPS":
            case "DEFVAR":
                if (count($instructionParts) != 2) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "var", $instruction);
                break;
            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                if (count($instructionParts) != 2) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", NULL, $instruction);
                break;
            //2 argumenty
            case "STRLEN":
            case "TYPE":
            case "MOVE":
            case "INT2CHAR";
            case "NOT":
                if (count($instructionParts) != 3) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "var", $instruction);
                argParser($instructionParts[2], "arg2", NULL, $instruction);
                break;
            case "READ":
                if (count($instructionParts) != 3) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "var", $instruction);
                argParser($instructionParts[2], "arg2", "type", $instruction);
                break;
            //3 argumenty
            case "ADD":
            case "SUB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                if (count($instructionParts) != 4) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "var", $instruction);
                argParser($instructionParts[2], "arg2", NULL, $instruction);
                argParser($instructionParts[3], "arg3", NULL, $instruction);
                break;
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                if (count($instructionParts) != 4) {
                    fwrite(STDERR, "Chybna syntaxe instrukci zdrojoveho kodu!\n");
                    exit(Errors::ERROR_LEXICAL_ERROR);
                }
                argParser($instructionParts[1], "arg1", "label", $instruction);
                argParser($instructionParts[2], "arg2", NULL, $instruction);
                argParser($instructionParts[3], "arg3", NULL, $instruction);
                break;
            default:
                fwrite(STDERR, "Neznamy nebo chybny operacni kod ve zdrojovem kodu!\n");
                exit(Errors::ERROR_WRONG_OPCODE);
        }
}

if ($headerChecked == false) {
    fwrite(STDERR, "Chybna nebo chybejici hlavicka zdrojoveho kodu!\n");
    exit(Errors::ERROR_WRONG_HEADER);
}

//--------->Generování XML reprezentace programu<----------//
print_r($dom->saveXML());
exit(0);