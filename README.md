# RadBio - softwarový nástroj pro odhad kontaminace rostlinné  biomasy na území zasaženém jadernou havárií

*Po radiační havárii mohou být radionuklidy kontaminovány rozsáhlé plochy určené k zemědělské produkci, a tím velmi omezeny možnosti využívání krajiny. Obnovení zemědělské činnosti na zasaženém území proto bude jednou z hlavních priorit. K tomu by měl pomoci i vyvinutý software RadBio, umožňující odhadnout kontaminaci biomasy rostlin na základě informací o půdních charakteristikách a velikosti kontaminace půdy.*

**Rychlé odkazy na software - [instalační soubory a návod k instalaci najdete zde](/stazeni_software.md).**


**Video na Youtube:**

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/vM-sRPEXvow/0.jpg)](https://www.youtube.com/watch?v=vM-sRPEXvow)

**RadBio** je volně šiřitelný softwarový nástroj umožňující předpovědět kontaminaci rostlin radionuklidy na základě informací o velikosti kontaminace půdy a půdních charakteristikách obhospodařované půdy, který je určen pro pozdní fázi jaderné havárie, kdy dochází ke kontaminaci rostlin radionuklidy přes kořenový systém. 

SW **RadBio** se skládá ze 2 samostatných částí **RadBio-JE** a **RadBio-CR**. 

**RadBio-JE** (SW pro okolí JE) je tvořen existující desktopovou aplikací QGIS, doplněnou o vyvinutý plugin (v jazyce Python) a detailní datové sady pro prostorovou vizualizaci predikce aktivity RN v rostlinách pro zadaný rok po havárii pro celou oblast okolí EDU a ETE rozdělenou na díly půdních bloků, jež jsou charakterizovány sadou atributů s hodnotami.

**RadBio-CR** (SW pro celou ČR) je tvořen desktopovou aplikací vytvořenou v jazyce Python s tabulkovým a grafickým výstupem pro predikci aktivity RN v rostlinách a jejího časového vývoje v závislosti na vstupních hodnotách zadaných uživatelem. 

Software RadBio je jedním z výsledků projektu výzkumu a vývoje "[Optimalizace postupů pro realizaci rostlinné výroby na území zasaženém jadernou havárií (VI20192022153)](https://starfos.tacr.cz/cs/project/VI20192022153)" řešeného v programu Bezpečnostní výzkum České republiky, jehož poskytovatelem je Ministerstvo vnitra České Republiky.

<img src="Images/logo_MV.png" alt="logo Ministerstva vnitra České Republiky" width="400"/>

Řešiteli projektu jsou:

[Státní ústav radiační ochrany, v.v.i.](https://www.suro.cz/cz/vyzkum)

[Česká zemědělská univerzita v Praze / Fakulta životního prostředí](https://www.fzp.czu.cz/cs/r-6897-veda-a-vyzkum)

[ENKI, o.p.s.](https://www.enki.cz/cs/projekty)

[Jihočeská univerzita v Českých Budějovicích / Zemědělská fakulta](https://www.fzt.jcu.cz/cz/veda-a-vyzkum/vyzkumna-temata)

<img src="Images/loga_web.png" alt="loga řešitelů projektu" width="600"/>

## Softwarové nástroje RadBio-CR a RadBio-JE
- oba nástroje jsou multiplatformní, byly úspěšně provozovány na PC s operačními systémy MS Windows 10 a Kubuntu GNU/Linux, funkčnost v systému Apple MacOS nebylo možné otestovat


### RadBio-CR

<img src="Images/SW-CR_GUI_thumb.jpg" alt="grafické rozhraní aplikace RadBio-ČR" width="800"/>

- standalone desktop aplikace s grafickým rozhraním, v jazyce [Python](https://www.python.org/) (SW byl testován na OS Windows 10, Python 3.10 a Kubuntu GNU/Linux Kubuntu 20.04 LTS + Python 3.8)
- software vyžaduje knihovny PyQt5, matplotlib, pandas, openpyxl (dostupné prostřednictvím Pip instalátoru v rámci Pythonu)
- bez mapové vizualizace
- výstup formou grafu / tabulky, možnost exportu výsledků ve formátu MS Excel

### RadBio-JE <img src="Images/RadBio_JE_icon.png" alt="ikona RadBio-JE"/>

<img src="Images/SW_JE_GUI_thumb.jpg" alt="grafické rozhraní aplikace RadBio-JE" width="800"/>

- plugin pro desktop software [QGIS](https://www.qgis.org/) (open-source, GNU-GPL)
- mapovou funkcionalitu poskytuje QGIS (testováno na QGIS verze 3.16 a vyšší)
- plugin se stará o specializované výpočty
- potřeba jsou mapové podklady se vstupními parametry (vektorové polygonové vrstvy s příslušnými atributy)


Software byl vytvořen ve spolupráci s Institutem radiobiologie, Gomel, Bělorusko.

Kód obou programů byl testován nástrojem Bandit, žádné nedostatky nebyly zjištěny.

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Oba programy jsou poskytovány pod open-source licencí [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html), neoficiální český překlad licence je [k dispozici zde](https://jxself.org/translations/gpl-3.cz.shtml)
