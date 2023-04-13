
## RadBio-ČR - systémové a programové požadavky

**podporované operační systémy:**
- MS Windows (testováno na 64bit OS Windows 10 Home / Professional)
- GNU/linux (testováno na Kubuntu linux verzí 20.04 LTS a 22.04.2 LTS)
- ?Mac OS - funkčnost v systému Mac OS nebylo možné otestovat

**Python + knihovny:**
- nástroj RadBio-ČR vyžaduje nainstalovaný Python, otestováno bylo s verzí 3.10 - [instalační soubor pro 64bit Windows stáhnete zde](https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe), vyžaduje admin práva
- software vyžaduje knihovny PyQt5, matplotlib, pandas, openpyxl, které se instalují pomocí vlastního nástroje v Pythonu, nevyžaduje admin práva

## Instalace Pythonu a knihoven

**Python**
- instalace probíhá standarně jako u jakéhokoliv Windows programu,  vyžaduje admin práva
- při instalaci je potřeba dole v okně Python instalátoru zaškrtnout “Install launcher...” a “Add Python 3.10 to PATH” *

**Python knihovny**
- software vyžaduje knihovny PyQt5, matplotlib, pandas, openpyxl
- ve Windows je tedy potřeba spustit program "Příkazový řádek" (též zvaný "cmd", najdete v Nabídce start nebo pomocí vyhledávání)
- do cmd následně zadáme příkaz:
       
    > pip3 install PyQt5 

- a potvrdíme klávesou Enter
- analogicky musíme zopakovat pro zbytek knihoven, tedy postupně zadat:

    > pip3 install matplotlib
    > 
    > pip3 install pandas
    > 
    > pip3 install openpyxl

## Instalace RadBio-ČR

- samotný nástroj RadBio-ČR se neinstaluje, stačí pouze stažený [ZIP soubor](https://github.com/juhele/RadBio/blob/main/RadBio-CR/2023_01_17_RadBio_CR_1.0.zip) (stáhnete kliknutím na tlačítko Download), rozbalit na disk v počítači a program spustit dvojklikem na soubor RadBio_CR.py

**Podrobný postup instalace vč. obrázků najdete v [dokumentaci](https://github.com/juhele/RadBio/blob/main/RadBio%20-%20Dokumentace%20k%20SW%20-%20k%2030.1.23.pdf) od strany 8**
