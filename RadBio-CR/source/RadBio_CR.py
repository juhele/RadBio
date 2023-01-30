import io
import json
import math
import sys
import zipfile
import pandas

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

# The Qt::AA_EnableHighDpiScaling application attribute, introduced in Qt 5.6, enables automatic scaling based on the
# monitor's pixel density.
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

# Enable High-DPI pixmaps
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# Barevná paleta + funkce na iterování skrz ni
class Colors:
    def __init__(self):
        # Původní barvy nahrazeny čitelnějšími 12/09/22
        # self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        #               '#bcbd22', '#17becf', '#1a55FF']
        self.colors = ['#b24502', '#b80058', '#008cf9', '#ebac23', '#006e00', '#ff9287', '#00bbad']
        self.maxcolors = len(self.colors)
        self.index = 0

    def next(self):
        if self.index == self.maxcolors - 1:
            self.index = 0
        else:
            self.index += 1
        return self.colors[self.index]

    def prev(self):
        if self.index < 0:
            self.index = self.maxcolors - 1
        else:
            self.index -= 1
        return self.colors[self.index]

    def first(self):
        self.index = 0
        return self.colors[self.index]

    def last(self):
        self.index = self.maxcolors - 1
        return self.colors[self.index]

    def current(self):
        return self.colors[self.index]


# Nástroj na iteraci: Použito na procházení stylů vykreslujících čar v grafu, aby se střídala tečkovaná, čárkovaná atd.
class Looper:
    def __init__(self, items):
        self.items = items
        self.current = 0

    def __iter__(self):
        return self.items[self.current]

    def __next__(self):
        self.current += 1
        if self.current > len(self.items) - 1:
            self.current = 0
        return self.items[self.current]


# Dialogové okno k změně defaultních hodnot (druhá záložka)
class UplatnitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Změna výchozích parametrů")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Opravdu chcete provést přepočet s novými hodnotami?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


# Navigační lišta
class MyToolBar(NavigationToolbar):
    NavigationToolbar.toolitems = (
        ('Domov', 'Obnovit původní zobrazení', 'home', 'home'),
        ('Dozadu', 'Zpět na předchozí zobrazení ', 'back', 'back'),
        ('Vpřed', 'Vpřed k dalšímu zobrazení', 'forward', 'forward'),
        (None, None, None, None),
        ('Posouvání', 'Posouvání os levou myší, zoomování pravou', 'move', 'pan'),
        ('Přiblížit', 'Přiblížit na obdélník', 'zoom_to_rect', 'zoom'),
        #
        # ('Subplots', 'Nastavení grafů', 'subplots', 'configure_subplots'),
        ('Nastavení grafu', 'Nastavení grafu', 'qt4_editor_options', 'edit_parameters'),
        (None, None, None, None),
        ('Uložit', 'Uložte obrázek', 'filesave', 'save_figure'),
    )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.archive = zipfile.ZipFile('params/params.zip', 'r') # Rozbalit parametry ze ZIPu
        self.showInfo() # Informační okno: obsah definovaný níže, ukáže okýnko s logem

        # Načtení grafického rozhraní:
        filedata = self.archive.read('mainwindow.ui')
        form = io.StringIO(filedata.decode('utf-8'))
        uic.loadUi(form, self)
        form.close()
        # -----
        # self.setFixedSize(self.size())
        # Parametry hlavního okna programu + prvky, které nebyly definovány v souboru .ui
        self.setWindowTitle('RadBio ČR - Software pro predikci obsahu radionuklidů v rostlinách ')
        self.figure = Figure(tight_layout=True, dpi=100)
        self.axes = self.figure.add_subplot()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self.plotwidget)
        self.toolbar = MyToolBar(self.canvas, self.toolwidget)
        self.model = QtGui.QStandardItemModel(self) # Něco jako databáze/tabulka, třída, do které se ukládají data

        # The invisible root item provides access to the model’s top-level items through the QStandardItem API,
        # making it possible to write functions that can treat top-level items and their children in a uniform way;
        # for example, recursive functions involving a tree model.
        self.model.invisibleRootItem()
        # -----

        # load databases: Funkce read_ jsou definované dál v kódu
        self.list_rostlin = {}
        self.b_cs_agrch = self.read_CS_AGRCH()
        self.b_cs_time = self.read_CS_TIME()
        self.b_sr_agrch = self.read_SR_AGRCH()
        self.b_sr_time = self.read_SR_TIME()
        self.b_pu_agrch = self.read_PU_AGRCH()
        self.b_pu_time = self.read_PU_TIME()
        self.b_c_puda = self.read_C_PUDA()
        self.short_puda = cut_pudy_to_orna(self.b_c_puda)
        # load databases ---
        self.init_components()
        # init for fist time
        # dataset
        self.data = {}
        self.title = 'empty'
        self.dict_koeff = dict()

        # dataset
        self.uplatnitZmeny()
        self.funkce_tk_changed()
        # Connectors - Vstupní Data
        self.sb_let_po_havarie.valueChanged.connect(self.createGraph)
        # Volba funkce TK
        self.cb_funkce_tk.currentIndexChanged.connect(self.funkce_tk_changed)
        self.cb_typ_pudy.currentIndexChanged.connect(self.agrch_changed)  # (self.createGraph)
        self.cb_druh_pudy.currentIndexChanged.connect(self.agrch_changed)
        self.chb_agregovany.stateChanged.connect(self.chb_agregovany_state)

        # Volba AGRCH
        self.cb_kultura.currentIndexChanged.connect(self.agrch_changed)
        self.cb_druh_pudy_2.currentIndexChanged.connect(self.agrch_druh_changed)
        self.sb_ph.valueChanged.connect(self.createGraph)
        self.sb_cox.valueChanged.connect(self.createGraph)
        self.sb_ca.valueChanged.connect(self.createGraph)
        self.sb_k.valueChanged.connect(self.createGraph)
        self.sb_mg.valueChanged.connect(self.createGraph)
        self.sb_p.valueChanged.connect(self.createGraph)

        # Aktivita v pude
        self.sb_cs.valueChanged.connect(self.createGraph)
        self.sb_sr.valueChanged.connect(self.createGraph)
        self.sb_pu.valueChanged.connect(self.createGraph)

        self.btn_vynulovat_cs.clicked.connect(self.vynulovat_aktivitu_cs)
        self.btn_vynulovat_sr.clicked.connect(self.vynulovat_aktivitu_sr)
        self.btn_vynulovat_pu.clicked.connect(self.vynulovat_aktivitu_pu)

        # Volba zaverecnych parametru
        self.dsb_c_klima.valueChanged.connect(self.createGraph)
        self.dsb_nf.valueChanged.connect(self.createGraph)
        self.exportButton.clicked.connect(self.exportVysledku)

        # ---- Záložka "Nastavení hodnot koeficientů" - tlačítka
        self.Btn_ResetPolocas.clicked.connect(self.set_defualtni_hodnoty_polocas)
        self.Btn_ResetCPuda.clicked.connect(self.set_defaultni_cpuda)
        self.Btn_ResetCOstatni.clicked.connect(self.set_defaultni_costatni)
        self.zmenyButton.clicked.connect(self.uplatnitClicked)
        self.defaultniButton.clicked.connect(self.set_defaultni_hodnoty_agrch)
    # Definice funkcí

    def vynulovat_aktivitu_cs(self):
        self.sb_cs.setValue(0)
        self.createGraph()

    def vynulovat_aktivitu_sr(self):
        self.sb_sr.setValue(0)
        self.createGraph()

    def vynulovat_aktivitu_pu(self):
        self.sb_pu.setValue(0)
        self.createGraph()

    # Volba funkce TK: "Použít agregovaný TK"
    def chb_agregovany_state(self):
        if self.chb_agregovany.isChecked():
            self.cb_kultura.setDisabled(True)
            self.cb_druh_pudy_2.setDisabled(True)
            self.sb_ph.setDisabled(True)
            self.sb_cox.setDisabled(True)
            self.sb_ca.setDisabled(True)
            self.sb_k.setDisabled(True)
            self.sb_mg.setDisabled(True)
            self.sb_p.setDisabled(True)
            self.tab_2.setDisabled(True)
            self.dsb_c_klima.setValue(1.0)
            self.dsb_c_klima.setDisabled(True)
        else:
            self.cb_kultura.setEnabled(True)
            self.cb_druh_pudy_2.setEnabled(True)
            self.sb_ph.setEnabled(True)
            self.sb_cox.setEnabled(True)
            self.sb_ca.setEnabled(True)
            self.sb_k.setEnabled(True)
            self.sb_mg.setEnabled(True)
            self.sb_p.setEnabled(True)
            self.tab_2.setEnabled(True)
            self.dsb_c_klima.setEnabled(True)
        self.createGraph()

    # Info okénko při spuštění: Logo + text
    def showInfo(self):
        logo_mv = QPixmap()
        logo_mv.loadFromData(self.archive.read('mv_cr.png'))
        msgBox = QMessageBox()
        msgBox.setIconPixmap(logo_mv.scaledToHeight(128, QtCore.Qt.SmoothTransformation))
        msgBox.setText("Vývoj programu RadBio-CR byl podpořen z projektu Ministerstva vnitra ČR VI20192022153")
        msgBox.setWindowTitle("Vítejte v programu RadBio-CR")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.button(QMessageBox.Ok).hide()
        QTimer.singleShot(5000, msgBox.close)
        msgBox.exec_()

    # Nastavení původních hodnot na záložce "Nastavení hodnot koeficientů"
    def set_defualtni_hodnoty_polocas(self):
        cs_def: float = 30.167
        sr_def: float = 28.797
        pu_def: float = 6561

        self.i_cs_polocas.setValue(cs_def)
        self.i_sr_polocas.setValue(sr_def)
        self.i_pu_polocas.setValue(pu_def)

    def set_defaultni_cpuda(self):
        cs_a: float = -0.5
        cs_b: float = 1
        sr_a: float = -0.5
        sr_b: float = 1
        pu_a: float = -0.5
        pu_b: float = 1

        self.i_cpuda_cs_a.setValue(cs_a)
        self.i_cpuda_cs_b.setValue(cs_b)
        self.i_cpuda_sr_a.setValue(sr_a)
        self.i_cpuda_sr_b.setValue(sr_b)
        self.i_cpuda_pu_a.setValue(pu_a)
        self.i_cpuda_pu_b.setValue(pu_b)

    def set_defaultni_costatni(self):
        cs_a: float = 1
        cs_b: float = -0.02
        sr_a: float = 1
        sr_b: float = -0.02
        pu_a: float = 1
        pu_b: float = -0.02

        self.i_costatni_cs_a.setValue(cs_a)
        self.i_costatni_cs_b.setValue(cs_b)
        self.i_costatni_sr_a.setValue(sr_a)
        self.i_costatni_sr_b.setValue(sr_b)
        self.i_costatni_pu_a.setValue(pu_a)
        self.i_costatni_pu_b.setValue(pu_b)

    def set_defaultni_hodnoty_agrch(self):
        # Nastavení defaultních hodnot
        minPh: float = 2.5
        maxPh: float = 9.0
        minCox: float = 0
        maxCox: float = 6.6
        minCa: int = 30
        maxCa: int = 120000
        minK: int = 20
        maxK: int = 8500
        minMg: int = 10
        maxMg: int = 7200
        minP: int = 0
        maxP: int = 10000

        # Aplikování hodnot
        self.i_ph_dolni.setValue(minPh)
        self.i_ph_horni.setValue(maxPh)
        self.i_cox_dolni.setValue(minCox)
        self.i_cox_horni.setValue(maxCox)
        self.i_ca_dolni.setValue(minCa)
        self.i_ca_horni.setValue(maxCa)
        self.i_k_dolni.setValue(minK)
        self.i_k_horni.setValue(maxK)
        self.i_mg_dolni.setValue(minMg)
        self.i_mg_horni.setValue(maxMg)
        self.i_p_dolni.setValue(minP)
        self.i_p_horni.setValue(maxP)
        self.uplatnitZmeny()

    # Triggruje se při změně některých zadání
    def agrch_changed(self):
        self.init_agrh_values()
        self.cb_druh_pudy_2.setCurrentIndex(self.cb_druh_pudy.currentIndex())
        self.createGraph()

    def agrch_druh_changed(self):
        self.cb_druh_pudy.setCurrentIndex(self.cb_druh_pudy_2.currentIndex())

    def funkce_tk_changed(self):
        if self.cb_funkce_tk.currentData() == 1:
            self.cb_druh_pudy.setEnabled(False)
            self.cb_typ_pudy.setEnabled(True)
        else:
            self.cb_druh_pudy.setEnabled(True)
            self.cb_typ_pudy.setEnabled(False)
        self.createGraph()

    def uplatnitClicked(self):
        dlg = UplatnitDialog(self)
        if dlg.exec():
            self.uplatnitZmeny()

    def uplatnitZmeny(self):
        self.sb_ph.setRange(self.i_ph_dolni.value(), self.i_ph_horni.value())
        self.sb_cox.setRange(self.i_cox_dolni.value(), self.i_cox_horni.value())
        self.sb_ca.setRange(self.i_ca_dolni.value(), self.i_ca_horni.value())
        self.sb_k.setRange(self.i_k_dolni.value(), self.i_k_horni.value())
        self.sb_mg.setRange(self.i_mg_dolni.value(), self.i_mg_horni.value())
        self.sb_p.setRange(self.i_p_dolni.value(), self.i_p_horni.value())
        self.dict_koeff = {'i_cs_polocas': self.i_cs_polocas.value(), 'i_sr_polocas': self.i_sr_polocas.value(),
                           'i_pu_polocas': self.i_pu_polocas.value(), 'i_cpuda_cs_a': self.i_cpuda_cs_a.value(),
                           'i_cpuda_cs_b': self.i_cpuda_cs_b.value(), 'i_cpuda_sr_a': self.i_cpuda_sr_a.value(),
                           'i_cpuda_sr_b': self.i_cpuda_sr_b.value(), 'i_cpuda_pu_a': self.i_cpuda_pu_a.value(),
                           'i_cpuda_pu_b': self.i_cpuda_pu_b.value(), 'i_costatni_cs_a': self.i_costatni_cs_a.value(),
                           'i_costatni_cs_b': self.i_costatni_cs_b.value(),
                           'i_costatni_sr_a': self.i_costatni_sr_a.value(),
                           'i_costatni_sr_b': self.i_costatni_sr_b.value(),
                           'i_costatni_pu_a': self.i_costatni_pu_a.value(),
                           'i_costatni_pu_b': self.i_costatni_pu_b.value(), 'i_ph_dolni': self.i_ph_dolni.value(),
                           'i_ph_horni': self.i_ph_horni.value(), 'i_cox_dolni': self.i_cox_dolni.value(),
                           'i_cox_horni': self.i_cox_horni.value(), 'i_ca_dolni': self.i_ca_dolni.value(),
                           'i_ca_horni': self.i_ca_horni.value(), 'i_k_dolni': self.i_k_dolni.value(),
                           'i_k_horni': self.i_k_horni.value(), 'i_mg_dolni': self.i_mg_dolni.value(),
                           'i_mg_horni': self.i_mg_horni.value(), 'i_p_dolni': self.i_p_dolni.value(),
                           'i_p_horni': self.i_p_horni.value(), 'i_pocet_let': self.i_pocet_let.value()}
        self.createGraph()

    def exportVysledku(self):
        try:
            file = QFileDialog.getSaveFileName(self, 'Vyberte soubor pro uložení dat', "export.xlsx",
                                               "Excel files (*.xlsx)",
                                               options=QFileDialog.DontUseNativeDialog)
            (pf, _) = file
            df = pandas.DataFrame(self.data)
            df1 = pandas.DataFrame(self.title)
            with pandas.ExcelWriter(pf) as writer:
                df.to_excel(writer, sheet_name='Aktivita v rostlině')
                df1.to_excel(writer, sheet_name='vstupni data')
        except:
            print('no export')

    def resizeEvent(self, event):
        size = event.size()
        newwidth = size.width() - self.VLayoutDiagram.geometry().x() - 30

        #newwidth = size.width() - self.verticalLayout_3.geometry().x() - 30
        #newheight = size.height() - 130
        newheight = size.height() - self.VLayoutDiagram.geometry().y() - 130
        self.canvas.resize(QSize(newwidth, newheight))
        #self.canvas.resize(QSize(800, 600))
        self.toolbar.setStyleSheet("QToolBar { border: 1px solid black; background: white;}")
        self.toolbar.setStyleSheet("QToolButton { background: white;}")
        self.toolbar.setGeometry(QtCore.QRect(0, 0, newwidth - 100, 40))

    def create_list(self):
        listok = []
        rostliny = self.get_rostliny()
        for items in rostliny.items():
            idx, need = items
            i = need['Popis']
            listok.append(i)
        return listok

    def init_components(self):
        self.init_cb_funkce_tk()
        self.init_cb_typ_pudy()
        self.init_cb_druh_pudy()
        self.init_cb_druh_pudy_2()
        self.init_cb_kultura()
        self.init_tree_rostliny()
        self.init_agrh_values()

    def passing(self):
        self.sb_ph.disconnect()
        self.sb_cox.disconnect()
        self.sb_ca.disconnect()
        self.sb_k.disconnect()
        self.sb_mg.disconnect()
        self.sb_p.disconnect()

    def un_passing(self):
        self.sb_ph.valueChanged.connect(self.createGraph)
        self.sb_cox.valueChanged.connect(self.createGraph)
        self.sb_ca.valueChanged.connect(self.createGraph)
        self.sb_k.valueChanged.connect(self.createGraph)
        self.sb_mg.valueChanged.connect(self.createGraph)
        self.sb_p.valueChanged.connect(self.createGraph)

    # Triggruje se u agrch_changed a init_components
    def init_agrh_values(self):
        ipuda = self.short_puda[(self.cb_kultura.currentText(), self.cb_druh_pudy.currentText())]
        self.passing()
        self.sb_ph.setValue(float(ipuda['PH_prum']))
        self.sb_cox.setValue(float(ipuda['COX_prum']))
        self.sb_ca.setValue(float(ipuda['CA_prum']))
        self.sb_k.setValue(float(ipuda['K_prum']))
        self.sb_mg.setValue(float(ipuda['MG_prum']))
        self.sb_p.setValue(float(ipuda['P_prum']))
        self.un_passing()

    def createGraph(self):
        # inicializace
        linestyles = Looper(['dotted', 'dashed', 'dashdot'])
        c = Colors()
        # vstupni data
        let_po_havarie: int = self.sb_let_po_havarie.value()
        let_do_predikce: int = self.i_pocet_let.value()
        funkce_tk: int = self.cb_funkce_tk.currentData()
        v_typ_pudy: int = self.cb_typ_pudy.currentText()
        v_druh_pudy: int = self.cb_druh_pudy.currentText()
        v_kultura = self.cb_kultura.currentText()
        use_TKagr: bool = self.chb_agregovany.isChecked()
        v_ph: float = self.sb_ph.value()
        v_cox: float = self.sb_cox.value()
        v_ca: float = self.sb_ca.value()
        v_k: float = self.sb_k.value()
        v_mg: float = self.sb_mg.value()
        v_p: float = self.sb_p.value()
        v_cs: float = self.sb_cs.value()
        v_sr: float = self.sb_sr.value()
        v_pu: float = self.sb_pu.value()
        c_klima: float = self.dsb_c_klima.value()
        nasobichi_faktor: float = self.dsb_nf.value()
        self.axes.clear()
        self.data.clear()
        funkce_tk_str = lambda a: str(v_typ_pudy) if a < 2 else str(v_druh_pudy)
        # decoration
        r_color = {}
        r_iter = 0
        # decoration

        try:
            x = range(let_do_predikce)
            for rostlina_id in self.list_rostlin:
                tloustka_cary = 2.5 # Nastavení tloušťky čar v grafu
                rostlina = {rostlina_id: self.list_rostlin[rostlina_id]}

                y1 = []
                y2 = []
                y3 = []

                l1, l2, l3 = calculations(let_po_havarie, let_do_predikce, funkce_tk, v_typ_pudy, v_druh_pudy,
                                          v_kultura, v_ph, v_cox, v_ca, v_k, v_mg, v_p, v_cs, v_sr, v_pu, y1, y2, y3,
                                          c_klima, nasobichi_faktor, rostlina, self.short_puda, self.b_cs_agrch,
                                          self.b_sr_agrch, self.b_pu_agrch, self.b_cs_time, self.b_sr_time,
                                          self.b_pu_time, use_TKagr, self.dict_koeff)
                # Změna 12/09/22 Z původního plot na semilogy
                self.axes.semilogy(x, l1, label=self.list_rostlin[rostlina_id], color=c.next(), linestyle='dashed',
                                   linewidth=tloustka_cary)
                self.axes.semilogy(x, l2, color=c.current(), linestyle='dashdot', linewidth=tloustka_cary)
                self.axes.semilogy(x, l3, color=c.current(), linestyle='dotted', linewidth=tloustka_cary)
                self.data[('Předpověď aktivity v rostlině', '', 'Počet let po havárii', '', '')] = ''
                self.data[('', '', str(let_po_havarie), 'Rok', '')] = x
                self.data[(self.list_rostlin[rostlina_id], '', '', 'Cs-137', 'Bq/kg')] = pandas.Series(l1)
                self.data[(self.list_rostlin[rostlina_id], '', '', 'Sr-90', 'Bq/kg')] = pandas.Series(l2)
                self.data[(self.list_rostlin[rostlina_id], '', '', 'Pu-240', 'Bq/kg')] = pandas.Series(l3)
                r_color[r_iter] = c.current()
                r_iter += 1

            maximum = []
            for key in self.data.keys():
                try:
                    if key == ('', '', str(let_po_havarie), 'Rok', ''):
                        pass
                    else:
                        maximum.append(max(self.data[key]))
                except:
                    maximum.append(0)

            # self.axes.axis([0, max(x), 0, max(maximum)])
            self.axes.axis(xmin=0, xmax=max(x), ymax=max(maximum))

        except:
            #print('Zadne rostliny')
            pass  # print('no rostliny')

        if funkce_tk == 1:
            d_puda = ', Typ: ' + str(v_typ_pudy)
        else:
            d_puda = ', Druh: ' + str(v_druh_pudy)

        # vytvorit zahlavi
        try:
            if self.chb_agregovany.isChecked():
                self.title = {('Půda', 'Funkce TK podle' + self.funkce_podle(funkce_tk) + ' půdy'): [
                    funkce_tk_str(funkce_tk)],
                    ('Půda', 'Použit agregovaný TK'): [self.pouzit_TKagr(self.chb_agregovany.isChecked())],
                    ('Agrochemie', 'Kultura'): 'NA',
                    ('Agrochemie', 'Druh'): 'NA',
                    ('Agrochemie', 'Ph'): 'NA',
                    ('Agrochemie', 'Cox'): 'NA',
                    ('Agrochemie', 'Ca'): 'NA',
                    ('Agrochemie', 'K'): 'NA',
                    ('Agrochemie', 'Mg'): 'NA',
                    ('Agrochemie', 'P'): 'NA',
                    (' ', 'Roky po havárii'): [let_po_havarie],
                    ('Aktivita v půdě Bq/m^2', 'Cs-137'): [int(v_cs)],
                    ('Aktivita v půdě Bq/m^2', 'Sr-90'): [int(v_sr)],
                    ('Aktivita v půdě Bq/m^2', 'Pu-240'): [int(v_pu)],
                    ('Faktori', 'C_Klima'): [round(c_klima, 2)],
                    ('Faktori', 'NF'): [round(nasobichi_faktor, 2)],
                    ('Faktori', 'Cpuda_CS_a'): 'NA',
                    ('Faktori', 'Cpuda_CS_b'): 'NA',
                    ('Faktori', 'Cpuda_Sr_a'): 'NA',
                    ('Faktori', 'Cpuda_Sr_b'): 'NA',
                    ('Faktori', 'Cpuda_Pu_a'): 'NA',
                    ('Faktori', 'Cpuda_Pu_b'): 'NA',
                    ('Faktori', 'Costatni_CS_a'): 'NA',
                    ('Faktori', 'Costatni_CS_b'): 'NA',
                    ('Faktori', 'Costatni_Sr_a'): 'NA',
                    ('Faktori', 'Costatni_Sr_b'): 'NA',
                    ('Faktori', 'Costatni_Pu_a'): 'NA',
                    ('Faktori', 'Costatni_Pu_b'): 'NA'
                }
                title: str = 'Předpověď hmotnostní aktivity radionuklidů v rostlinách\nPočet let po havárii:{0:5} ' \
                             'Použit agregovaný TK:{1:5} Funkce TK:{2:18}\nAgrochemie: Kultura:{3:15} Druh půdy:{4:5}' \
                             '\nPh={5:7} Cox={6:7} Ca={7:7} K={8:7} Mg={9:7} P={10:7}' \
                             '\nAktivita v půdě (Bq/m2): Cs-137={11:15} Sr-90={12:15} Pu-240={13:15}' \
                             '\nCklima={14:10} NF={15:10}'.format(str(let_po_havarie),
                                                                  self.pouzit_TKagr(self.chb_agregovany.isChecked()),
                                                                  self.title_funkce_podle(funkce_tk), 'NA', 'NA',
                                                                  'NA', 'NA', 'NA', 'NA', 'NA', 'NA',
                                                                  str(int(v_cs)), str(int(v_sr)), str(int(v_pu)),
                                                                  'NA', str(round(nasobichi_faktor, 2)))
            else:
                self.title = {('Půda', 'Funkce TK podle' + self.funkce_podle(funkce_tk) + ' půdy'): [
                    funkce_tk_str(funkce_tk)],
                    ('Půda', 'Použit agregovaný TK'): [self.pouzit_TKagr(self.chb_agregovany.isChecked())],
                    ('Agrochemie', 'Kultura'): [str(v_kultura)],
                    ('Agrochemie', 'Druh'): [str(v_druh_pudy)],
                    ('Agrochemie', 'Ph'): [round(v_ph, 1)],
                    ('Agrochemie', 'Cox'): [round(v_cox, 2)],
                    ('Agrochemie', 'Ca'): [round(v_ca)],
                    ('Agrochemie', 'K'): [round(v_k)],
                    ('Agrochemie', 'Mg'): [round(v_mg, 1)],
                    ('Agrochemie', 'P'): [round(v_p, 1)],
                    (' ', 'Roky po havárii'): [let_po_havarie],
                    ('Aktivita v půdě Bq/m^2', 'Cs-137'): [int(v_cs)],
                    ('Aktivita v půdě Bq/m^2', 'Sr-90'): [int(v_sr)],
                    ('Aktivita v půdě Bq/m^2', 'Pu-240'): [int(v_pu)],
                    ('Faktori', 'C_Klima'): [round(c_klima, 2)],
                    ('Faktori', 'NF'): [round(nasobichi_faktor, 2)],
                    ('Faktori', 'Cpuda_CS_a'): [round(self.dict_koeff['i_cpuda_cs_a'], 2)],
                    ('Faktori', 'Cpuda_CS_b'): [round(self.dict_koeff['i_cpuda_cs_b'], 2)],
                    ('Faktori', 'Cpuda_Sr_a'): [round(self.dict_koeff['i_cpuda_sr_a'], 2)],
                    ('Faktori', 'Cpuda_Sr_b'): [round(self.dict_koeff['i_cpuda_sr_b'], 2)],
                    ('Faktori', 'Cpuda_Pu_a'): [round(self.dict_koeff['i_cpuda_pu_a'], 2)],
                    ('Faktori', 'Cpuda_Pu_b'): [round(self.dict_koeff['i_cpuda_pu_b'], 2)],
                    ('Faktori', 'Costatni_CS_a'): [round(self.dict_koeff['i_costatni_cs_a'], 2)],
                    ('Faktori', 'Costatni_CS_b'): [round(self.dict_koeff['i_costatni_cs_b'], 2)],
                    ('Faktori', 'Costatni_Sr_a'): [round(self.dict_koeff['i_costatni_sr_a'], 2)],
                    ('Faktori', 'Costatni_Sr_b'): [round(self.dict_koeff['i_costatni_sr_b'], 2)],
                    ('Faktori', 'Costatni_Pu_a'): [round(self.dict_koeff['i_costatni_pu_a'], 2)],
                    ('Faktori', 'Costatni_Pu_b'): [round(self.dict_koeff['i_costatni_pu_b'], 2)]
                }
                title: str = 'Předpověď hmotnostní aktivity radionuklidů v rostlinách\nPočet let po havárii:{0:5} ' \
                             'Použit agregovaný TK:{1:5} Funkce TK:{2:18}\nAgrochemie: Kultura:{3:15} Druh půdy:{4:5}' \
                             '\nPh={5:7} Cox={6:7} Ca={7:7} K={8:7} Mg={9:7} P={10:7}' \
                             '\nAktivita v půdě (Bq/m2): Cs-137={11:15} Sr-90={12:15} Pu-240={13:15}' \
                             '\nCklima={14:10} NF={15:10}'.format(str(let_po_havarie),
                                                                  self.pouzit_TKagr(self.chb_agregovany.isChecked()),
                                                                  self.title_funkce_podle(funkce_tk), str(v_kultura),
                                                                  str(v_druh_pudy), str(round(v_ph, 1)),
                                                                  str(round(v_cox, 2)), str(round(v_ca)),
                                                                  str(round(v_k)), str(round(v_mg, 1)),
                                                                  str(round(v_p, 1)), str(int(v_cs)), str(int(v_sr)),
                                                                  str(int(v_pu)), str(round(c_klima, 2)),
                                                                  str(round(nasobichi_faktor, 2)))
        except:
            title: str = ''

        self.axes.set_title(title, {'size': 13})
        # vytvorit zahlavi
        self.axes.set_xlabel('Čas, rok', {'size': 13})
        self.axes.set_ylabel('Hmotnostní aktivita, Bq/kg', {'size': 13})
        # Nastavení zobrazení legendy

        lineCs = Line2D([0,1],[0,1],linestyle="dashed", linewidth=3, color='k')
        lineSr = Line2D([0,1],[0,1],linestyle='dashdot', linewidth=3, color='k')
        linePu = Line2D([0,1],[0,1],linestyle='dotted', linewidth=3, color='k')
        line_catalogue = [lineCs, lineSr, linePu]
        line_descript = ["Cs-137", "Sr-90", "Pu-240"]
        leg = self.axes.legend(fontsize='x-large', handlelength=0, framealpha=1.0, fancybox=False, loc="upper right")
        self.figure.gca().add_artist(leg)
        # decorator
        for item in r_color.keys():
            leg.texts[item].set_color(r_color[item])

        self.axes.legend(line_catalogue, line_descript, fontsize='x-large', fancybox=False, framealpha=1.0, loc="lower left")

        # decorator
        self.axes.grid(True)
        self.canvas.draw()

    def funkce_podle(self, funkce_tk):
        if funkce_tk == 1:
            return ' typu'
        if funkce_tk == 2:
            return ' druhu'

    def title_funkce_podle(self, funkce_tk):
        if funkce_tk == 1:
            return 'typ půdy - {0}'.format(str(self.cb_typ_pudy.currentText()))
        if funkce_tk == 2:
            return 'druh půdy - {0}'.format(str(self.cb_druh_pudy.currentText()))

    def pouzit_TKagr(self, pouzit_TKagr):
        if pouzit_TKagr:
            return 'Ano'
        else:
            return 'Ne'

    # Nastavení nabídky - Typ nebo Druh půdy
    def init_cb_funkce_tk(self):
        self.cb_funkce_tk.clear()
        self.cb_funkce_tk.addItem('Typ půdy', 1)
        # self.cb_funkce_tk.setItemData(0, 1)
        self.cb_funkce_tk.addItem('Druh půdy', 2)
        # self.cb_funkce_tk.setItemData(1, 2)

    # Nastavení nabídky PT01 - PT15
    def init_cb_typ_pudy(self):
        self.cb_typ_pudy.clear()
        for i in range(1, 10):
            self.cb_typ_pudy.addItem('PT0' + str(i))
            self.cb_typ_pudy.setItemData(i - 1, i)
        for i in range(10, 16):
            self.cb_typ_pudy.addItem('PT' + str(i))
            self.cb_typ_pudy.setItemData(i - 1, i)

    # Nastavení nabídky druh půdy v sekci "Volba funkce TK"
    def init_cb_druh_pudy(self):
        self.cb_druh_pudy.clear()
        idx = 0
        for i in 'ABCDE':
            self.cb_druh_pudy.addItem(i)
            self.cb_druh_pudy.setItemData(idx, idx + 1)
            idx += 1

    # Nastavení nabídky druh půdy v sekci "Volba AGRCH"
    def init_cb_druh_pudy_2(self):
        self.cb_druh_pudy_2.clear()
        idx = 0
        for i in 'ABCDE':
            self.cb_druh_pudy_2.addItem(i)
            self.cb_druh_pudy_2.setItemData(idx, idx + 1)
            idx += 1

    # Volba AGRCH: Kultura
    def init_cb_kultura(self):
        self.cb_kultura.clear()
        self.cb_kultura.addItem('orná půda')
        self.cb_kultura.setItemData(0, 1)
        self.cb_kultura.addItem('chmelnice')
        self.cb_kultura.setItemData(1, 2)
        self.cb_kultura.addItem('vinice')
        self.cb_kultura.setItemData(2, 3)
        self.cb_kultura.addItem('ovocný sad')
        self.cb_kultura.setItemData(3, 4)
        self.cb_kultura.addItem('TTP')
        self.cb_kultura.setItemData(4, 5)

    # Rozklikávací strom v sloupečku "Vybrat rostlinu"
    def init_tree_rostliny(self):
        global rootitem, subrootitem
        skupina = ''
        podskupina = ''
        rostliny = self.get_rostliny()
        for items in rostliny.items():
            idx, need = items
            skupina_new = str(need['Skupina'])
            podskupina_new = str(need['Podskupina'])
            druh_new = str(need['Druh_rostliny'])
            field_data = int(need['Id'])
            field_tip = str(need['Popis'])
            if skupina_new != skupina:
                rootitem = QtGui.QStandardItem(skupina_new)
                field_text = skupina_new
                skupina = skupina_new
                rootitem.setText(field_text)
                rootitem.setData(field_data)
                rootitem.setCheckable(True)
                rootitem.setEditable(False)
                rootitem.setToolTip(field_tip)
                self.model.appendRow(rootitem)
            else:
                if podskupina_new != podskupina:
                    subrootitem = QtGui.QStandardItem(podskupina_new)
                    field_text = podskupina_new
                    podskupina = podskupina_new
                    subrootitem.setText(field_text)
                    subrootitem.setData(field_data)
                    subrootitem.setCheckable(True)
                    subrootitem.setEditable(False)
                    subrootitem.setToolTip(field_tip)
                    rootitem.appendRow(subrootitem)
                else:
                    field_text = druh_new
                    # my item
                    item_in = QtGui.QStandardItem()
                    item_in.setText(field_text)
                    item_in.setData(field_data)
                    item_in.setCheckable(True)
                    item_in.setEditable(False)
                    item_in.setToolTip(field_tip)
                    # my item
                    subrootitem.appendRow(item_in)

        self.model.setHorizontalHeaderLabels(['rostliny'])
        self.tw_rostliny.setModel(self.model)
        self.tw_rostliny.header().hide()
        self.model.itemChanged.connect(self.setup_container)

    # Funkce triggrující načtení dat po zakliknutí položky ve stromu + okamžitá aktualizace grafu
    def setup_container(self, item):
        if item.checkState() == Qt.Checked:
            self.list_rostlin.update({item.data(): item.text()})
        else:
            del self.list_rostlin[item.data()]
        self.createGraph()

    # Načtení stromu do nabídky, strom je definovaný v souboru json
    # rostliny.json de facto definuje všechny koncové volby, přičemž zahrnuje i možnosti jako "vyber všechno"
    # u každého záznamu je vypsaná celá taxonomie
    def get_rostliny(self):
        archive = zipfile.ZipFile('params/params.zip', 'r')
        filedata = archive.read('rostliny.json')

        base: dict = {}
        data: dict = json.loads(filedata)

        if 'rostliny' in data:
            rostliny: dict = data['rostliny']
            i = 0
            for rostlina in rostliny:
                i = i + 1
                rstln = {}
                for key, value in rostlina.items():
                    rstln[key] = value
                base[i] = rstln
        return base

    #########################################
    ## Čtení jednotlivých datových souborů ##

    def read_CS_AGRCH(self):
        archive = zipfile.ZipFile('params/params.zip', 'r')
        filedata = archive.read('cs-agrch.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'cs_agrch' in data:
            lines: dict = data['cs_agrch']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_CS_TIME(self):
        filedata = self.archive.read('cs-time.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'cs_time' in data:
            lines: dict = data['cs_time']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_SR_AGRCH(self):
        filedata = self.archive.read('sr-agrch.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'sr_agrch' in data:
            lines: dict = data['sr_agrch']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_SR_TIME(self):
        filedata = self.archive.read('sr-time.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'sr_time' in data:
            lines: dict = data['sr_time']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_PU_AGRCH(self):
        filedata = self.archive.read('pu-agrch.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'pu_agrch' in data:
            lines: dict = data['pu_agrch']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_PU_TIME(self):
        filedata = self.archive.read('pu-time.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'pu_time' in data:
            lines: dict = data['pu_time']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    def read_C_PUDA(self):
        filedata = self.archive.read('c-puda.json')
        base: dict = {}
        data: dict = json.loads(filedata)

        if 'c_puda' in data:
            lines: dict = data['c_puda']
            base = {}
            i = 0
            for line in lines:
                i = i + 1
                lin = {}
                for key, value in line.items():
                    lin[key] = value
                base[i] = lin
        return base

    # -----------------------------------------


# ????
def cut_pudy_to_orna(dictionary: dict):
    n_puda: dict = {}
    for ipuda in dictionary.values():
        n_puda[(ipuda['Kultura'], ipuda['Druh_pudy'])] = ipuda
    return n_puda


# Pomocná funkce k výpočtům
def corr_Index(index: float):
    if index < 0:
        return 0
    if index > 1:
        return 1
    return index


# Výpočty
def calculations(let_po_havarie, let_do_predikce, funkce_tk, v_typ_pudy, v_druh_pudy, v_kultura, v_ph, v_cox,
                 v_ca, v_k, v_mg, v_p, v_cs, v_sr, v_pu, v1, v2, v3, c_klima, nasobichi_faktor, rostlina,
                 db_short_puda, db_cs_agrch, db_sr_agrch, db_pu_agrch, db_cs_time, db_sr_time, db_pu_time, use_TKagr,
                 params):
    # Cpuda
    ipuda = db_short_puda[(v_kultura, v_druh_pudy)]
    puda_PH_opt = float(ipuda['PH_opt'])
    puda_PH_min = float(ipuda['PH_min'])
    puda_COX_opt = float(ipuda['COX_opt'])
    puda_COX_min = float(ipuda['COX_min'])
    puda_CA_opt = float(ipuda['CA_opt'])
    puda_CA_min = float(ipuda['CA_min'])
    puda_K_opt = float(ipuda['K_opt'])
    puda_K_min = float(ipuda['K_min'])
    puda_MG_opt = float(ipuda['MG_opt'])
    puda_MG_min = float(ipuda['MG_min'])
    puda_P_opt = float(ipuda['P_opt'])
    puda_P_min = float(ipuda['P_min'])

    I_ph = corr_Index((v_ph - puda_PH_min) / (puda_PH_opt - puda_PH_min))
    I_cox = corr_Index((v_cox - puda_COX_min) / (puda_COX_opt - puda_COX_min))
    I_ca = corr_Index((v_ca - puda_CA_min) / (puda_CA_opt - puda_CA_min))
    I_k = corr_Index((v_k - puda_K_min) / (puda_K_opt - puda_K_min))
    I_mg = corr_Index((v_mg - puda_MG_min) / (puda_MG_opt - puda_MG_min))
    I_p = corr_Index((v_p - puda_P_min) / (puda_P_opt - puda_P_min))

    I_zurodneni = (I_ph + I_cox + I_ca + I_k + I_mg + I_p) / 6

    # Cpuda
    # a = -0.5, b = 1
    if use_TKagr:
        Cpuda_cs = 1
        Cpuda_sr = 1
        Cpuda_pu = 1
    else:
        cs_a_puda = params['i_cpuda_cs_a']
        cs_b_puda = params['i_cpuda_cs_b']
        sr_a_puda = params['i_cpuda_sr_a']
        sr_b_puda = params['i_cpuda_sr_b']
        pu_a_puda = params['i_cpuda_pu_a']
        pu_b_puda = params['i_cpuda_pu_b']
        Cpuda_cs = cs_a_puda * I_zurodneni + cs_b_puda
        Cpuda_sr = sr_a_puda * I_zurodneni + sr_b_puda
        Cpuda_pu = pu_a_puda * I_zurodneni + pu_b_puda
    # Cpuda

    # rostlina ID
    for parser in rostlina.items():
        rostlina_id, rostlina_txt = parser
    # rostlina ID

    # TKagrch
    if use_TKagr:
        TKagrch_CS = 1
        TKagrch_SR = 1
        TKagrch_PU = 1
    else:
        # CS
        cs_agrodata = db_cs_agrch[int(rostlina_id)]
        cs_agrch_a = float(cs_agrodata['AGRCH_' + v_druh_pudy + '_a1'])
        cs_agrch_b = float(cs_agrodata['AGRCH_' + v_druh_pudy + '_b1'])
        TKagrch_CS = cs_agrch_a * math.exp(cs_agrch_b * v_k)

        # SR
        sr_agrodata = db_sr_agrch[int(rostlina_id)]
        sr_agrch_a = float(sr_agrodata['AGRCH_' + v_druh_pudy + '_a1'])
        sr_agrch_b = float(sr_agrodata['AGRCH_' + v_druh_pudy + '_b1'])
        TKagrch_SR = sr_agrch_a * math.exp(sr_agrch_b * v_ph)

        # PU
        pu_agrodata = db_pu_agrch[int(rostlina_id)]
        pu_agrch_a = float(pu_agrodata['AGRCH_' + v_druh_pudy + '_a1'])
        pu_agrch_b = float(pu_agrodata['AGRCH_' + v_druh_pudy + '_b1'])
        TKagrch_PU = pu_agrch_a * math.exp(pu_agrch_b * v_ph)
    # TKagrch

    # Init databases for TKtime
    cs_timedata = db_cs_time[int(rostlina_id)]
    sr_timedata = db_sr_time[int(rostlina_id)]
    pu_timedata = db_pu_time[int(rostlina_id)]

    # Polocas
    cs_polocas = params['i_cs_polocas']
    sr_polocas = params['i_sr_polocas']
    pu_polocas = params['i_pu_polocas']
    # Polocas

    for year in range(let_po_havarie, let_po_havarie + let_do_predikce):
        # Cpremenna
        Cpremenna_cs = math.exp(- 0.693147181 * (year - let_po_havarie) / cs_polocas)
        Cpremenna_sr = math.exp(- 0.693147181 * (year - let_po_havarie) / sr_polocas)
        Cpremenna_pu = math.exp(- 0.693147181 * (year - let_po_havarie) / pu_polocas)

        # Costatni
        if use_TKagr:
            Costatni_cs = 1
            Costatni_sr = 1
            Costatni_pu = 1
        else:
            cs_a_ostatni = params['i_costatni_cs_a']
            cs_b_ostatni = params['i_costatni_cs_b']
            sr_a_ostatni = params['i_costatni_sr_a']
            sr_b_ostatni = params['i_costatni_sr_b']
            pu_a_ostatni = params['i_costatni_pu_a']
            pu_b_ostatni = params['i_costatni_pu_b']
            Costatni_cs = cs_a_ostatni * math.exp(cs_b_ostatni * (year - let_po_havarie))
            Costatni_sr = sr_a_ostatni * math.exp(sr_b_ostatni * (year - let_po_havarie))
            Costatni_pu = pu_a_ostatni * math.exp(pu_b_ostatni * (year - let_po_havarie))
        # Costatni

        # TKtime
        # CS
        if funkce_tk == 1:
            if year < int(cs_timedata[v_typ_pudy + '_rp1']):
                cs_time_a = float(cs_timedata[v_typ_pudy + '_a1'])
                cs_time_b = float(cs_timedata[v_typ_pudy + '_b1'])
            elif year < int(cs_timedata[v_typ_pudy + '_rp2']):
                cs_time_a = float(cs_timedata[v_typ_pudy + '_a2'])
                cs_time_b = float(cs_timedata[v_typ_pudy + '_b2'])
            elif year < int(cs_timedata[v_typ_pudy + '_rp3']):
                cs_time_a = float(cs_timedata[v_typ_pudy + '_a3'])
                cs_time_b = float(cs_timedata[v_typ_pudy + '_b3'])
            else:
                cs_time_a = float(cs_timedata[v_typ_pudy + '_a3'])
                cs_time_b = float(cs_timedata[v_typ_pudy + '_b3'])
        elif funkce_tk == 2:
            if year < int(cs_timedata[v_druh_pudy + '_rp1']):
                cs_time_a = float(cs_timedata[v_druh_pudy + '_a1'])
                cs_time_b = float(cs_timedata[v_druh_pudy + '_b1'])
            elif year < int(cs_timedata[v_druh_pudy + '_rp2']):
                cs_time_a = float(cs_timedata[v_druh_pudy + '_a2'])
                cs_time_b = float(cs_timedata[v_druh_pudy + '_b2'])
            elif year < int(cs_timedata[v_druh_pudy + '_rp3']):
                cs_time_a = float(cs_timedata[v_druh_pudy + '_a3'])
                cs_time_b = float(cs_timedata[v_druh_pudy + '_b3'])
            else:
                cs_time_a = float(cs_timedata[v_druh_pudy + '_a3'])
                cs_time_b = float(cs_timedata[v_druh_pudy + '_b3'])
        TKtime_CS = cs_time_a * math.exp(cs_time_b * year)

        # SR
        if funkce_tk == 1:
            if year < int(sr_timedata[v_typ_pudy + '_rp1']):
                sr_time_a = float(sr_timedata[v_typ_pudy + '_a1'])
                sr_time_b = float(sr_timedata[v_typ_pudy + '_b1'])
            elif year < int(sr_timedata[v_typ_pudy + '_rp2']):
                sr_time_a = float(sr_timedata[v_typ_pudy + '_a2'])
                sr_time_b = float(sr_timedata[v_typ_pudy + '_b2'])
            elif year < int(sr_timedata[v_typ_pudy + '_rp3']):
                sr_time_a = float(sr_timedata[v_typ_pudy + '_a3'])
                sr_time_b = float(sr_timedata[v_typ_pudy + '_b3'])
            else:
                sr_time_a = float(sr_timedata[v_typ_pudy + '_a3'])
                sr_time_b = float(sr_timedata[v_typ_pudy + '_b3'])
        elif funkce_tk == 2:
            if year < int(sr_timedata[v_druh_pudy + '_rp1']):
                sr_time_a = float(sr_timedata[v_druh_pudy + '_a1'])
                sr_time_b = float(sr_timedata[v_druh_pudy + '_b1'])
            elif year < int(sr_timedata[v_druh_pudy + '_rp2']):
                sr_time_a = float(sr_timedata[v_druh_pudy + '_a2'])
                sr_time_b = float(sr_timedata[v_druh_pudy + '_b2'])
            elif year < int(sr_timedata[v_druh_pudy + '_rp3']):
                sr_time_a = float(sr_timedata[v_druh_pudy + '_a3'])
                sr_time_b = float(sr_timedata[v_druh_pudy + '_b3'])
            else:
                sr_time_a = float(sr_timedata[v_druh_pudy + '_a3'])
                sr_time_b = float(sr_timedata[v_druh_pudy + '_b3'])
        TKtime_SR = sr_time_a * math.exp(sr_time_b * year)

        # PU
        if funkce_tk == 1:
            if year < int(pu_timedata[v_typ_pudy + '_rp1']):
                pu_time_a = float(pu_timedata[v_typ_pudy + '_a1'])
                pu_time_b = float(pu_timedata[v_typ_pudy + '_b1'])
            elif year < int(pu_timedata[v_typ_pudy + '_rp2']):
                pu_time_a = float(pu_timedata[v_typ_pudy + '_a2'])
                pu_time_b = float(pu_timedata[v_typ_pudy + '_b2'])
            elif year < int(pu_timedata[v_typ_pudy + '_rp3']):
                pu_time_a = float(pu_timedata[v_typ_pudy + '_a3'])
                pu_time_b = float(pu_timedata[v_typ_pudy + '_b3'])
            else:
                pu_time_a = float(pu_timedata[v_typ_pudy + '_a3'])
                pu_time_b = float(pu_timedata[v_typ_pudy + '_b3'])
        elif funkce_tk == 2:
            if year < int(pu_timedata[v_druh_pudy + '_rp1']):
                pu_time_a = float(pu_timedata[v_druh_pudy + '_a1'])
                pu_time_b = float(pu_timedata[v_druh_pudy + '_b1'])
            elif year < int(pu_timedata[v_druh_pudy + '_rp2']):
                pu_time_a = float(pu_timedata[v_druh_pudy + '_a2'])
                pu_time_b = float(pu_timedata[v_druh_pudy + '_b2'])
            elif year < int(pu_timedata[v_druh_pudy + '_rp3']):
                pu_time_a = float(pu_timedata[v_druh_pudy + '_a3'])
                pu_time_b = float(pu_timedata[v_druh_pudy + '_b3'])
            else:
                pu_time_a = float(pu_timedata[v_druh_pudy + '_a3'])
                pu_time_b = float(pu_timedata[v_druh_pudy + '_b3'])
        TKtime_PU = pu_time_a * math.exp(pu_time_b * year)
        # TKtime

        # Kalculace aktivity
        aktivita_Cs = v_cs * TKtime_CS * TKagrch_CS * Cpremenna_cs * Cpuda_cs * Costatni_cs * c_klima * nasobichi_faktor
        aktivita_Sr = v_sr * TKtime_SR * TKagrch_SR * Cpremenna_sr * Cpuda_sr * Costatni_sr * c_klima * nasobichi_faktor
        aktivita_Pu = v_pu * TKtime_PU * TKagrch_PU * Cpremenna_pu * Cpuda_pu * Costatni_pu * c_klima * nasobichi_faktor
        v1.append(aktivita_Cs)
        v2.append(aktivita_Sr)
        v3.append(aktivita_Pu)

    return v1, v2, v3


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.resize(main.width() + 1, main.height() + 1)
    sys.exit(app.exec_())
