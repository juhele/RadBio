## RadBio-JE - systémové a programové požadavky

**podporované ooperační systémy:**
- MS Windows (testováno na 64bit OS Windows 10 Home / Professional)
- GNU/linux (testováno na Kubuntu linux verzí 20.04 LTS a 22.04.2 LTS)
- funkčnost v systému Mac OS nebylo možné otestovat

**program QGIS**
- nástroj RadBio-JE vyžaduje nainstalovaný program QGIS
- pro firemní použití je doporučována aktuální LTR verze QGIS 3.28.5 'Firenze'- [instalační soubor pro 64bit Windows stáhnete zde](https://qgis.org/downloads/QGIS-OSGeo4W-3.28.5-1.msi), další varianty instalačních balíčků (např. pro systémy GNU/Linux a Mac OS) jsou k dispozici na  [webu QGIS.org](https://www.qgis.org/en/site/forusers/download.html)
- QGIS je open-source (licence GNU-GPL) tj. lze bezplatně používat i komerčně, není potřeba žádná registrace ani aktivace licence

## Instalace RadBio-JE

Abyste mohli nástroj RadBio-JE používat,  potřebujete open-source program QGIS, který si bezplatně - pro firemní použití je doporučována aktuální LTR verze QGIS 3.28.5 'Firenze'- [instalační soubor pro 64bit Windows stáhnete zde](https://qgis.org/downloads/QGIS-OSGeo4W-3.28.5-1.msi), další varianty instalačních balíčků (např. pro systémy GNU/Linux a Mac OS) jsou k dispozici na  [webu QGIS.org](https://www.qgis.org/en/site/forusers/download.html). Podrobný postup instalace najdete v [dokumentaci](https://github.com/juhele/RadBio/blob/main/RadBio%20-%20Dokumentace%20k%20SW%20-%20k%2030.1.23.pdf) od strany 13. Program byl testován na 64bit OS Windows 10 Home / Professional a Kubuntu linux verzí 20.04 LTS a 22.04.2 LTS, funkčnost v systému Mac OS nebylo možné otestovat.


## Fiktivní demo data pro testování software RadBio-JE

Jedná se o datovou vrstvu formátu [OGC GeoPackage](https://www.geopackage.org/), v souřadnicovém systému [WGS 84 / UTM zone 33N (EPSG:32633)](https://epsg.io/32633). Struktura dat odpovídá “ostrým” datům, demo data jsou tedy vhodná nejen k vyzkoušení software, ale také jako šablona pro vytvoření vlastní vrstvy vstupních dat.

Hranice políček jsou fiktivní, nicméně respektují hranice reálných administrativních jednotek ČR (data [RÚIAN](https://www.cuzk.cz/ruian/)), tj. údaje o katastru, kraji ap. odpovídají realitě. 

Klimatická data. Srážková i teplotní data byla získána z [otevřených dat, která uvolnil Český hydrometeorologický ústav (ČHMÚ)](https://www.chmi.cz/historicka-data/pocasi/denni-data/Denni-data-dle-z.-123-1998-Sb). Atributy byly získány zpracováním denních dat ze stanic ČHMÚ za období 1991-2020 vlastními prostředky - využit byl software [R-Project](https://www.r-project.org/), [SAGA GIS](https://saga-gis.sourceforge.io/en/index.html) a další. SW v současné době klimatická data nevyužívá.

Data o radioaktivní kontaminaci půdy (plošná aktivita radionuklidů Cs-137, Sr-90, Pu-240 ve spadu, Bq/m2). Hodnoty plošných aktivit uvedených radionuklidů jsou fiktivní; všechny byly odvozeny z plošné kontaminace Cs-137 zjištěné krátce po černobylské havárii.

Data typů a druhů půd a hodnoty agrochemických charakteristik jsou fiktivní, neodpovídají reálné situaci.

Podrobnosti tvorby demo dat jsou uvedeny v [Dokumentaci k SW](https://github.com/juhele/RadBio/blob/main/RadBio%20-%20Dokumentace%20k%20SW%20-%20k%2030.1.23.pdf).

