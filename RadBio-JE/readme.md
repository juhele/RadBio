## RadBio-JE - systémové a programové požadavky

*Informace na úvod - pro používání software RadBio-ČR musí mít uživatel alespoň základní zkušenost s programy typu [GIS](https://cs.wikipedia.org/wiki/Geografick%C3%BD_informa%C4%8Dn%C3%AD_syst%C3%A9m) - když ne přímo s programem [QGIS](https://cs.wikipedia.org/wiki/QGIS), tak alespoň s podobným - jako je např. [ArcGIS](https://cs.wikipedia.org/wiki/ArcGIS), tj. jisté základní znalosti týkající se práce s geografickými daty, vrstvami ap.*

**podporované operační systémy:**
- MS Windows (testováno na 64bit OS Windows 10 Home / Professional)
- GNU/linux (testováno na Kubuntu linux verzí 20.04 LTS a 22.04.2 LTS)
- ?Mac OS - funkčnost v systému Mac OS nebylo možné otestovat

**program QGIS**
- nástroj RadBio-JE vyžaduje nainstalovaný program QGIS
- pro firemní použití je doporučována aktuální LTR verze QGIS 3.28.5 'Firenze'- [instalační soubor pro 64bit Windows stáhnete zde](https://qgis.org/downloads/QGIS-OSGeo4W-3.28.5-1.msi), další varianty instalačních balíčků (např. pro systémy GNU/Linux a Mac OS) jsou k dispozici na  [webu QGIS.org](https://www.qgis.org/en/site/forusers/download.html)
- QGIS je open-source (licence GNU-GPL) tj. lze bezplatně používat i komerčně, není potřeba žádná registrace ani aktivace licence

## Instalace RadBio-JE

Nástroj RadBio-JE je tzv. plugin / zásuvný modul pro QGIS - [ZIP soubor s pluginem stáhnete zde](https://github.com/juhele/RadBio/blob/main/RadBio-JE/sw_je_QGIS_plugin_v1_0.zip) kliknutím na tlačítko Download, instalace probíhá přímo z nerozbaleného ZIP souboru přes menu QGISu:

*Zásuvné moduly / Zpráva a instalace Zásuvných modulů / Instalovat ze ZIPu*

Podrobný postup instalace vč. obrázků najdete v [dokumentaci](https://github.com/juhele/RadBio/blob/main/RadBio%20-%20Dokumentace%20k%20SW%20-%20k%2030.1.23.pdf) od strany 13. 


## Snadno použitelné online podkladové mapy pro QGIS


*Varianta a)*
- myší chytněte v soubor *.qlr v této složce a přetáhněte ho do mapového okna QGISu

*Varianta b)*
- spustťe QGIS a vrstvu přidejte přes hlavní menu: Vrstva / Přidat vrstvu z definičního souboru

Systémové a programové požadavky

- nainstalovaný program QGIS verze 3.x

- připojení k internetu - qlr soubor funguje podobně jako zástupce, jen uživateli ušetří nutnost ručně konfigurovat připojení k online mapovému zdroji nebo nutnost instalovat QGIS plugin typu OpenLayers či QuickMapServices


## Fiktivní demo data pro testování software RadBio-JE

Jedná se o datovou vrstvu formátu [OGC GeoPackage](https://www.geopackage.org/), v souřadnicovém systému [WGS 84 / UTM zone 33N (EPSG:32633)](https://epsg.io/32633). Struktura dat odpovídá “ostrým” datům, demo data jsou tedy vhodná nejen k vyzkoušení software, ale také jako šablona pro vytvoření vlastní vrstvy vstupních dat.

Hranice políček jsou fiktivní, nicméně respektují hranice reálných administrativních jednotek ČR (data [RÚIAN](https://www.cuzk.cz/ruian/)), tj. údaje o katastru, kraji ap. odpovídají realitě. 

Klimatická data. Srážková i teplotní data byla získána z [otevřených dat, která uvolnil Český hydrometeorologický ústav (ČHMÚ)](https://www.chmi.cz/historicka-data/pocasi/denni-data/Denni-data-dle-z.-123-1998-Sb). Atributy byly získány zpracováním denních dat ze stanic ČHMÚ za období 1991-2020 vlastními prostředky - využit byl software [R-Project](https://www.r-project.org/), [SAGA GIS](https://saga-gis.sourceforge.io/en/index.html) a další. SW v současné době klimatická data nevyužívá.

Data o radioaktivní kontaminaci půdy (plošná aktivita radionuklidů Cs-137, Sr-90, Pu-240 ve spadu, Bq/m2). Hodnoty plošných aktivit uvedených radionuklidů jsou fiktivní; všechny byly odvozeny z plošné kontaminace Cs-137 zjištěné krátce po černobylské havárii.

Data typů a druhů půd a hodnoty agrochemických charakteristik jsou fiktivní, neodpovídají reálné situaci.

Podrobnosti tvorby demo dat jsou uvedeny v [Dokumentaci k SW](https://github.com/juhele/RadBio/blob/main/RadBio_-_Dokumentace_k_SW.pdf).

