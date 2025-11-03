from __future__ import annotations

import requests
import urllib.parse
from bs4 import BeautifulSoup

from enum import Enum, Flag, auto
from dataclasses import dataclass, asdict, is_dataclass
from json import dumps as jsonDumps, JSONEncoder

class DataclassJSONEncoder(JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)  # handles nested dataclasses
        if isinstance(obj, (Enum, Flag)):
            return str(obj)      # or use obj.value if you prefer numbers
        return super().default(obj)

import datetime
from dateutil.parser import parse as parse_date

API_BASE_URL="https://w3.srbvoz.rs/redvoznje//api"
WEB_BASE_URL="https://w3.srbvoz.rs/redvoznje"

class TrainException(Exception):
    def __init__(self, message, errors=[]):            
        super().__init__(f"Train API exception occured: {message}")
            
        self.errors = errors

class TrainType(Enum):
    COMMUTER_TRAIN=1,
    INTER_CITY=2,
    REGIONAL_TRAIN=3

    @staticmethod
    def parse(str_: str) -> TrainType:
        match str_:
            case "BG:VOZ":
                return TrainType.COMMUTER_TRAIN
    
            case "REGIO VOZ":
                return TrainType.REGIONAL_TRAIN
    
            case "BRZI VOZ":
                return TrainType.INTER_CITY
            
            case "REGIO EXPRES":
                return TrainType.INTER_CITY
            
            case _:
                TrainException("Unknown train type")

class Station(Enum):
    KEMENDIN_ST = {'name': 'Kemendin st', 'id': '01016', 'safe name': 'KEMENDIN_ST'}
    ALTINA_ST = {'name': 'Altina st', 'id': '01017', 'safe name': 'ALTINA_ST'}
    DOLJEVAC = {'name': 'DOLJEVAC', 'id': '11001', 'safe name': 'DOLJEVAC'}
    KOCANE = {'name': 'KOCANE', 'id': '11002', 'safe name': 'KOCANE'}
    PUKOVAC = {'name': 'PUKOVAC', 'id': '11003', 'safe name': 'PUKOVAC'}
    BRESTOVAC = {'name': 'BRESTOVAC', 'id': '11004', 'safe name': 'BRESTOVAC'}
    LIPOVICA = {'name': 'LIPOVICA', 'id': '11005', 'safe name': 'LIPOVICA'}
    PECENJEVCE = {'name': 'PEČENJEVCE', 'id': '11006', 'safe name': 'PECENJEVCE'}
    ZIVKOVO = {'name': 'ŽIVKOVO', 'id': '11007', 'safe name': 'ZIVKOVO'}
    LESKOVAC = {'name': 'LESKOVAC', 'id': '11050', 'safe name': 'LESKOVAC'}
    SAJINOVAC = {'name': 'ŠAJINOVAC', 'id': '11101', 'safe name': 'SAJINOVAC'}
    JASENICA = {'name': 'JASENICA', 'id': '11102', 'safe name': 'JASENICA'}
    RECICA = {'name': 'REČICA', 'id': '11104', 'safe name': 'RECICA'}
    PODINA = {'name': 'PODINA', 'id': '11105', 'safe name': 'PODINA'}
    PROKUPLJE = {'name': 'PROKUPLJE', 'id': '11106', 'safe name': 'PROKUPLJE'}
    LUKOMIR = {'name': 'LUKOMIR', 'id': '11119', 'safe name': 'LUKOMIR'}
    TOPLICKI_BADNJEVAC = {'name': 'TOPLIČKI BADNJEVAC', 'id': '11121', 'safe name': 'TOPLICKI_BADNJEVAC'}
    ZITORADJA_CENTAR = {'name': 'ŽITORADJA CENTAR', 'id': '11129', 'safe name': 'ZITORADJA_CENTAR'}
    LESAK = {'name': 'LEŠAK', 'id': '12001', 'safe name': 'LESAK'}
    DREN = {'name': 'DREN', 'id': '12002', 'safe name': 'DREN'}
    LEPOSAVIC = {'name': 'LEPOSAVIĆ', 'id': '12003', 'safe name': 'LEPOSAVIC'}
    SOCANICA = {'name': 'SOČANICA', 'id': '12004', 'safe name': 'SOCANICA'}
    IBARSKA_SLATINA = {'name': 'IBARSKA SLATINA', 'id': '12005', 'safe name': 'IBARSKA_SLATINA'}
    BANJSKA = {'name': 'BANJSKA', 'id': '12006', 'safe name': 'BANJSKA'}
    VALAC = {'name': 'VALAČ', 'id': '12007', 'safe name': 'VALAC'}
    ZVECAN = {'name': 'ZVEČAN', 'id': '12008', 'safe name': 'ZVECAN'}
    PLANDISTE = {'name': 'PLANDIŠTE', 'id': '12019', 'safe name': 'PLANDISTE'}
    PRIDVORICA = {'name': 'PRIDVORICA', 'id': '12021', 'safe name': 'PRIDVORICA'}
    KOSOVSKA_MITROVICA_SEVER = {'name': 'KOSOVSKA MITROVICA SEVER', 'id': '12022', 'safe name': 'KOSOVSKA_MITROVICA_SEVER'}
    MATARUSKA_BANJA = {'name': 'MATARUŠKA BANJA', 'id': '12101', 'safe name': 'MATARUSKA_BANJA'}
    PROGORELICA = {'name': 'PROGORELICA', 'id': '12102', 'safe name': 'PROGORELICA'}
    BOGUTOVACKA_BANJA = {'name': 'BOGUTOVAČKA BANJA', 'id': '12103', 'safe name': 'BOGUTOVACKA_BANJA'}
    POLUMIR = {'name': 'POLUMIR', 'id': '12105', 'safe name': 'POLUMIR'}
    USCE = {'name': 'UŠĆE', 'id': '12106', 'safe name': 'USCE'}
    JOSANICKA_BANJA = {'name': 'JOŠANIČKA BANJA', 'id': '12107', 'safe name': 'JOSANICKA_BANJA'}
    PISKANJA = {'name': 'PISKANJA', 'id': '12108', 'safe name': 'PISKANJA'}
    BRVENIK = {'name': 'BRVENIK', 'id': '12109', 'safe name': 'BRVENIK'}
    RVATI = {'name': 'RVATI', 'id': '12110', 'safe name': 'RVATI'}
    RASKA = {'name': 'RAŠKA', 'id': '12111', 'safe name': 'RASKA'}
    KAZNOVICI = {'name': 'KAZNOVIĆI', 'id': '12112', 'safe name': 'KAZNOVICI'}
    RUDNICA = {'name': 'RUDNICA', 'id': '12113', 'safe name': 'RUDNICA'}
    JERINA_STAJ = {'name': 'JERINA STAJ', 'id': '12114', 'safe name': 'JERINA_STAJ'}
    LOZNO = {'name': 'LOZNO', 'id': '12115', 'safe name': 'LOZNO'}
    PUSTO_POLJE = {'name': 'PUSTO POLJE', 'id': '12116', 'safe name': 'PUSTO_POLJE'}
    MRZENICA = {'name': 'MRZENICA', 'id': '12201', 'safe name': 'MRZENICA'}
    DEDINA = {'name': 'DEDINA', 'id': '12203', 'safe name': 'DEDINA'}
    KRUSEVAC = {'name': 'KRUŠEVAC', 'id': '12204', 'safe name': 'KRUSEVAC'}
    KOSEVI = {'name': 'KOŠEVI', 'id': '12205', 'safe name': 'KOSEVI'}
    STOPANJA = {'name': 'STOPANJA', 'id': '12207', 'safe name': 'STOPANJA'}
    POCEKOVINA = {'name': 'POCEKOVINA', 'id': '12208', 'safe name': 'POCEKOVINA'}
    TRSTENIK = {'name': 'TRSTENIK', 'id': '12210', 'safe name': 'TRSTENIK'}
    VRNJACKA_BANJA = {'name': 'VRNJAČKA BANJA', 'id': '12211', 'safe name': 'VRNJACKA_BANJA'}
    LIPOVA_STA = {'name': 'LIPOVA STA', 'id': '12212', 'safe name': 'LIPOVA_STA'}
    PODUNAVCI = {'name': 'PODUNAVCI', 'id': '12213', 'safe name': 'PODUNAVCI'}
    VRBA_STAJ = {'name': 'VRBA STAJ', 'id': '12214', 'safe name': 'VRBA_STAJ'}
    RATINA = {'name': 'RATINA', 'id': '12215', 'safe name': 'RATINA'}
    TOMINAC_STA = {'name': 'TOMINAC STA', 'id': '12216', 'safe name': 'TOMINAC_STA'}
    VRANESI_STAJ = {'name': 'VRANEŠI STAJ', 'id': '12217', 'safe name': 'VRANESI_STAJ'}
    CITLUK = {'name': 'ČITLUK', 'id': '12218', 'safe name': 'CITLUK'}
    GRAD_STALAC_STA = {'name': 'GRAD STALAĆ STA', 'id': '12219', 'safe name': 'GRAD_STALAC_STA'}
    BELOTINCE = {'name': 'BELOTINCE', 'id': '12302', 'safe name': 'BELOTINCE'}
    MALOSISTE = {'name': 'MALOŠIŠTE', 'id': '12303', 'safe name': 'MALOSISTE'}
    CAPLJINAC = {'name': 'ČAPLJINAC', 'id': '12304', 'safe name': 'CAPLJINAC'}
    BRALJINA = {'name': 'BRALJINA', 'id': '12502', 'safe name': 'BRALJINA'}
    STARO_TRUBAREVO = {'name': 'STARO TRUBAREVO', 'id': '12503', 'safe name': 'STARO_TRUBAREVO'}
    DJUNIS = {'name': 'ĐUNIS', 'id': '12504', 'safe name': 'DJUNIS'}
    VITKOVAC_STAJ = {'name': 'VITKOVAC STAJ.', 'id': '12505', 'safe name': 'VITKOVAC_STAJ.'}
    DONJI_LJUBES = {'name': 'DONJI LJUBEŠ', 'id': '12506', 'safe name': 'DONJI_LJUBES'}
    KORMAN = {'name': 'KORMAN', 'id': '12507', 'safe name': 'KORMAN'}
    TRNJANI = {'name': 'TRNJANI', 'id': '12508', 'safe name': 'TRNJANI'}
    ADROVAC = {'name': 'ADROVAC', 'id': '12509', 'safe name': 'ADROVAC'}
    ALEKSINAC = {'name': 'ALEKSINAC', 'id': '12510', 'safe name': 'ALEKSINAC'}
    LUZANE = {'name': 'LUŽANE', 'id': '12511', 'safe name': 'LUZANE'}
    TESICA = {'name': 'TEŠICA', 'id': '12512', 'safe name': 'TESICA'}
    GREJAC = {'name': 'GREJAČ', 'id': '12513', 'safe name': 'GREJAC'}
    SUPOVACKI_MOST = {'name': 'SUPOVAČKI MOST', 'id': '12514', 'safe name': 'SUPOVACKI_MOST'}
    MEZGRAJA = {'name': 'MEZGRAJA', 'id': '12515', 'safe name': 'MEZGRAJA'}
    TRUPALE = {'name': 'TRUPALE', 'id': '12516', 'safe name': 'TRUPALE'}
    CEROVO_RAZANJ = {'name': 'CEROVO RAŽANJ', 'id': '12517', 'safe name': 'CEROVO_RAZANJ'}
    VRTISTE = {'name': 'VRTIŠTE', 'id': '12518', 'safe name': 'VRTISTE'}
    GORNJI_LJUBES = {'name': 'GORNJI LJUBEŠ', 'id': '12519', 'safe name': 'GORNJI_LJUBES'}
    NOZRINA = {'name': 'NOZRINA', 'id': '12520', 'safe name': 'NOZRINA'}
    CRVENI_KRST = {'name': 'CRVENI KRST', 'id': '12550', 'safe name': 'CRVENI_KRST'}
    NIS = {'name': 'NIŠ', 'id': '12551', 'safe name': 'NIS'}
    ADRANI = {'name': 'ADRANI', 'id': '13001', 'safe name': 'ADRANI'}
    MRSAC = {'name': 'MRSAĆ', 'id': '13002', 'safe name': 'MRSAC'}
    SAMAILA = {'name': 'SAMAILA', 'id': '13003', 'safe name': 'SAMAILA'}
    GORICANI = {'name': 'GORIČANI', 'id': '13004', 'safe name': 'GORICANI'}
    MRSINCI = {'name': 'MRSINCI', 'id': '13005', 'safe name': 'MRSINCI'}
    ZABLACE = {'name': 'ZABLAĆE', 'id': '13006', 'safe name': 'ZABLACE'}
    PRIJEVOR = {'name': 'PRIJEVOR', 'id': '13007', 'safe name': 'PRIJEVOR'}
    OVCAR_BANJA = {'name': 'OVČAR BANJA', 'id': '13008', 'safe name': 'OVCAR_BANJA'}
    DRAGACEVO = {'name': 'DRAGAČEVO', 'id': '13009', 'safe name': 'DRAGACEVO'}
    TRBUSANI = {'name': 'TRBUŠANI', 'id': '13010', 'safe name': 'TRBUSANI'}
    BORACKO = {'name': 'BORAČKO', 'id': '13011', 'safe name': 'BORACKO'}
    BALUGA = {'name': 'BALUGA', 'id': '13012', 'safe name': 'BALUGA'}
    JELEN_DO = {'name': 'JELEN DO', 'id': '13013', 'safe name': 'JELEN_DO'}
    KUKICI = {'name': 'KUKIĆI', 'id': '13014', 'safe name': 'KUKICI'}
    GUGALJ_STA = {'name': 'GUGALJ STA', 'id': '13015', 'safe name': 'GUGALJ_STA'}
    CACAK = {'name': 'ČAČAK', 'id': '13060', 'safe name': 'CACAK'}
    BATOCINA = {'name': 'BATOČINA', 'id': '13201', 'safe name': 'BATOCINA'}
    GRADAC = {'name': 'GRADAC', 'id': '13202', 'safe name': 'GRADAC'}
    BADNJEVAC = {'name': 'BADNJEVAC', 'id': '13203', 'safe name': 'BADNJEVAC'}
    RESNIK_KRAGUJEVACKI = {'name': 'RESNIK KRAGUJEVAČKI', 'id': '13204', 'safe name': 'RESNIK_KRAGUJEVACKI'}
    MILATOVAC = {'name': 'MILATOVAC', 'id': '13205', 'safe name': 'MILATOVAC'}
    JOVANOVAC = {'name': 'JOVANOVAC', 'id': '13207', 'safe name': 'JOVANOVAC'}
    ZAVOD = {'name': 'ZAVOD', 'id': '13209', 'safe name': 'ZAVOD'}
    GROSNICA = {'name': 'GROŠNICA', 'id': '13210', 'safe name': 'GROSNICA'}
    DRAGOBRACA = {'name': 'DRAGOBRAĆA', 'id': '13211', 'safe name': 'DRAGOBRACA'}
    KNIC = {'name': 'KNIĆ', 'id': '13213', 'safe name': 'KNIC'}
    GRUZA = {'name': 'GRUŽA', 'id': '13214', 'safe name': 'GRUZA'}
    GUBEREVAC = {'name': 'GUBEREVAC', 'id': '13215', 'safe name': 'GUBEREVAC'}
    VITKOVAC = {'name': 'VITKOVAC', 'id': '13216', 'safe name': 'VITKOVAC'}
    MILAVCICI = {'name': 'MILAVČIĆI', 'id': '13217', 'safe name': 'MILAVCICI'}
    VITANOVAC = {'name': 'VITANOVAC', 'id': '13218', 'safe name': 'VITANOVAC'}
    SUMARICE = {'name': 'ŠUMARICE', 'id': '13219', 'safe name': 'SUMARICE'}
    SIRCA = {'name': 'SIRČA', 'id': '13220', 'safe name': 'SIRCA'}
    TOMICA_BRDO = {'name': 'TOMIĆA BRDO', 'id': '13221', 'safe name': 'TOMICA_BRDO'}
    KRAGUJEVAC = {'name': 'KRAGUJEVAC', 'id': '13250', 'safe name': 'KRAGUJEVAC'}
    KRALJEVO = {'name': 'KRALJEVO', 'id': '13251', 'safe name': 'KRALJEVO'}
    BRZAN = {'name': 'BRZAN', 'id': '13301', 'safe name': 'BRZAN'}
    MILOSEVO = {'name': 'MILOŠEVO', 'id': '13302', 'safe name': 'MILOSEVO'}
    BAGRDAN = {'name': 'BAGRDAN', 'id': '13303', 'safe name': 'BAGRDAN'}
    LANISTE = {'name': 'LANIŠTE', 'id': '13304', 'safe name': 'LANISTE'}
    BUKOVCE = {'name': 'BUKOVČE', 'id': '13305', 'safe name': 'BUKOVCE'}
    GILJE = {'name': 'GILJE', 'id': '13307', 'safe name': 'GILJE'}
    PARACIN = {'name': 'PARAĆIN', 'id': '13310', 'safe name': 'PARACIN'}
    SIKIRICA_RATARI = {'name': 'SIKIRICA-RATARI', 'id': '13311', 'safe name': 'SIKIRICA-RATARI'}
    DRENOVAC = {'name': 'DRENOVAC', 'id': '13312', 'safe name': 'DRENOVAC'}
    CICEVAC = {'name': 'ĆIĆEVAC', 'id': '13313', 'safe name': 'CICEVAC'}
    LUCINA = {'name': 'LUČINA', 'id': '13314', 'safe name': 'LUCINA'}
    JAGODINA = {'name': 'JAGODINA', 'id': '13350', 'safe name': 'JAGODINA'}
    CUPRIJA = {'name': 'ĆUPRIJA', 'id': '13351', 'safe name': 'CUPRIJA'}
    STALAC = {'name': 'STALAĆ', 'id': '13352', 'safe name': 'STALAC'}
    VELIKA_PLANA = {'name': 'VELIKA PLANA', 'id': '13401', 'safe name': 'VELIKA_PLANA'}
    STARO_SELO = {'name': 'STARO SELO', 'id': '13402', 'safe name': 'STARO_SELO'}
    NOVO_SELO = {'name': 'NOVO SELO', 'id': '13403', 'safe name': 'NOVO_SELO'}
    MARKOVAC = {'name': 'MARKOVAC', 'id': '13404', 'safe name': 'MARKOVAC'}
    LAPOVO_VAROS = {'name': 'LAPOVO VAROŠ', 'id': '13405', 'safe name': 'LAPOVO_VAROS'}
    LAPOVO_RANZ_STAJ = {'name': 'LAPOVO RANŽ.STAJ.', 'id': '13406', 'safe name': 'LAPOVO_RANZ.STAJ.'}
    LAPOVO = {'name': 'LAPOVO', 'id': '13450', 'safe name': 'LAPOVO'}
    MALA_KRSNA = {'name': 'MALA KRSNA', 'id': '13551', 'safe name': 'MALA_KRSNA'}
    GODOMIN = {'name': 'GODOMIN', 'id': '13602', 'safe name': 'GODOMIN'}
    RADINAC = {'name': 'RADINAC', 'id': '13603', 'safe name': 'RADINAC'}
    VRANOVO = {'name': 'VRANOVO', 'id': '13604', 'safe name': 'VRANOVO'}
    SMEDEREVO = {'name': 'SMEDEREVO', 'id': '13670', 'safe name': 'SMEDEREVO'}
    KOVACEVAC = {'name': 'KOVAČEVAC', 'id': '13701', 'safe name': 'KOVACEVAC'}
    RABROVAC = {'name': 'RABROVAC', 'id': '13702', 'safe name': 'RABROVAC'}
    KUSADAK = {'name': 'KUSADAK', 'id': '13703', 'safe name': 'KUSADAK'}
    RATARE = {'name': 'RATARE', 'id': '13704', 'safe name': 'RATARE'}
    GLIBOVAC = {'name': 'GLIBOVAC', 'id': '13705', 'safe name': 'GLIBOVAC'}
    PALANKA = {'name': 'PALANKA', 'id': '13706', 'safe name': 'PALANKA'}
    MALA_PLANA = {'name': 'MALA PLANA', 'id': '13707', 'safe name': 'MALA_PLANA'}
    MATEJEVAC = {'name': 'MATEJEVAC', 'id': '14001', 'safe name': 'MATEJEVAC'}
    PANTELEJ = {'name': 'PANTELEJ', 'id': '14003', 'safe name': 'PANTELEJ'}
    JASENOVIK = {'name': 'JASENOVIK', 'id': '14004', 'safe name': 'JASENOVIK'}
    GRAMADA = {'name': 'GRAMADA', 'id': '14005', 'safe name': 'GRAMADA'}
    HADZICEVO = {'name': 'HADŽIĆEVO', 'id': '14006', 'safe name': 'HADZICEVO'}
    SVRLJIG = {'name': 'SVRLJIG', 'id': '14007', 'safe name': 'SVRLJIG'}
    NISEVAC = {'name': 'NIŠEVAC', 'id': '14008', 'safe name': 'NISEVAC'}
    PALILULA = {'name': 'PALILULA', 'id': '14009', 'safe name': 'PALILULA'}
    SVRLJISKI_MILJKOVAC = {'name': 'SVRLJIŠKI MILJKOVAC', 'id': '14010', 'safe name': 'SVRLJISKI_MILJKOVAC'}
    PODVIS = {'name': 'PODVIS', 'id': '14011', 'safe name': 'PODVIS'}
    RGOSTE = {'name': 'RGOŠTE', 'id': '14012', 'safe name': 'RGOSTE'}
    KNJAZEVAC = {'name': 'KNJAŽEVAC', 'id': '14013', 'safe name': 'KNJAZEVAC'}
    GORNJE_ZUNICE = {'name': 'GORNJE ZUNIĆE', 'id': '14014', 'safe name': 'GORNJE_ZUNICE'}
    DONJE_ZUNICE = {'name': 'DONJE ZUNIĆE', 'id': '14015', 'safe name': 'DONJE_ZUNICE'}
    MINICEVO = {'name': 'MINIĆEVO', 'id': '14016', 'safe name': 'MINICEVO'}
    SELACKA_REKA = {'name': 'SELAČKA REKA', 'id': '14017', 'safe name': 'SELACKA_REKA'}
    MALI_IZVOR = {'name': 'MALI IZVOR', 'id': '14018', 'safe name': 'MALI_IZVOR'}
    VRATARNICA = {'name': 'VRATARNICA', 'id': '14019', 'safe name': 'VRATARNICA'}
    GRLJAN = {'name': 'GRLJAN', 'id': '14021', 'safe name': 'GRLJAN'}
    TIMOK = {'name': 'TIMOK', 'id': '14022', 'safe name': 'TIMOK'}
    ZAJECAR = {'name': 'ZAJEČAR', 'id': '14060', 'safe name': 'ZAJECAR'}
    TRNAVAC = {'name': 'TRNAVAC', 'id': '14101', 'safe name': 'TRNAVAC'}
    COKONJAR = {'name': 'ČOKONJAR', 'id': '14102', 'safe name': 'COKONJAR'}
    TABAKOVAC = {'name': 'TABAKOVAC', 'id': '14104', 'safe name': 'TABAKOVAC'}
    TABAKOVACKA_REKA = {'name': 'TABAKOVAČKA REKA', 'id': '14105', 'safe name': 'TABAKOVACKA_REKA'}
    BRUSNIK = {'name': 'BRUSNIK', 'id': '14106', 'safe name': 'BRUSNIK'}
    TAMNIC = {'name': 'TAMNIĆ', 'id': '14107', 'safe name': 'TAMNIC'}
    CRNOMASNICA = {'name': 'CRNOMASNICA', 'id': '14108', 'safe name': 'CRNOMASNICA'}
    RAJAC = {'name': 'RAJAC', 'id': '14109', 'safe name': 'RAJAC'}
    ROGLJEVO = {'name': 'ROGLJEVO', 'id': '14110', 'safe name': 'ROGLJEVO'}
    VELJKOVO = {'name': 'VELJKOVO', 'id': '14111', 'safe name': 'VELJKOVO'}
    KOBISNICA = {'name': 'KOBIŠNICA', 'id': '14113', 'safe name': 'KOBISNICA'}
    NEGOTIN = {'name': 'NEGOTIN', 'id': '14114', 'safe name': 'NEGOTIN'}
    PRAHOVO = {'name': 'PRAHOVO', 'id': '14115', 'safe name': 'PRAHOVO'}
    PRAHOVO_PRISTANISTE = {'name': 'PRAHOVO PRISTANIŠTE', 'id': '14170', 'safe name': 'PRAHOVO_PRISTANISTE'}
    VRAZOGRNAC = {'name': 'VRAŽOGRNAC', 'id': '14301', 'safe name': 'VRAZOGRNAC'}
    RGOTINA = {'name': 'RGOTINA', 'id': '14302', 'safe name': 'RGOTINA'}
    ZAGRADJE = {'name': 'ZAGRAĐE', 'id': '14303', 'safe name': 'ZAGRADJE'}
    BOR_TERETNA = {'name': 'BOR TERETNA', 'id': '14305', 'safe name': 'BOR_TERETNA'}
    MAJDANPEK = {'name': 'MAJDANPEK', 'id': '14401', 'safe name': 'MAJDANPEK'}
    LESKOVO = {'name': 'LESKOVO', 'id': '14402', 'safe name': 'LESKOVO'}
    JASIKOVO = {'name': 'JASIKOVO', 'id': '14403', 'safe name': 'JASIKOVO'}
    VLAOLE = {'name': 'VLAOLE', 'id': '14404', 'safe name': 'VLAOLE'}
    CEROVO = {'name': 'CEROVO', 'id': '14405', 'safe name': 'CEROVO'}
    KRIVELJSKI_POTOK = {'name': 'KRIVELJSKI POTOK', 'id': '14406', 'safe name': 'KRIVELJSKI_POTOK'}
    MALI_KRIVELJ = {'name': 'MALI KRIVELJ', 'id': '14407', 'safe name': 'MALI_KRIVELJ'}
    GORNJANE = {'name': 'GORNJANE', 'id': '14408', 'safe name': 'GORNJANE'}
    KRIVELJSKI_MOST = {'name': 'KRIVELJSKI MOST', 'id': '14409', 'safe name': 'KRIVELJSKI_MOST'}
    DEBELI_LUG = {'name': 'DEBELI LUG', 'id': '14410', 'safe name': 'DEBELI_LUG'}
    VLAOLE_SELO = {'name': 'VLAOLE SELO', 'id': '14411', 'safe name': 'VLAOLE_SELO'}
    SUSULAJKA = {'name': 'ŠUŠULAJKA', 'id': '14412', 'safe name': 'SUSULAJKA'}
    BREZONIK = {'name': 'BREZONIK', 'id': '14413', 'safe name': 'BREZONIK'}
    POZAREVAC = {'name': 'POŽAREVAC', 'id': '14550', 'safe name': 'POZAREVAC'}
    LJUBICEVSKI_MOST = {'name': 'LJUBIČEVSKI MOST', 'id': '14551', 'safe name': 'LJUBICEVSKI_MOST'}
    LASTRA = {'name': 'LASTRA', 'id': '15102', 'safe name': 'LASTRA'}
    SAMARI = {'name': 'SAMARI', 'id': '15103', 'safe name': 'SAMARI'}
    DRENOVACKI_KIK = {'name': 'DRENOVAČKI KIK', 'id': '15104', 'safe name': 'DRENOVACKI_KIK'}
    RAZANA = {'name': 'RAŽANA', 'id': '15105', 'safe name': 'RAZANA'}
    KOSJERIC = {'name': 'KOSJERIĆ', 'id': '15106', 'safe name': 'KOSJERIC'}
    KALENIC = {'name': 'KALENIĆ', 'id': '15107', 'safe name': 'KALENIC'}
    SEVOJNO = {'name': 'SEVOJNO', 'id': '15108', 'safe name': 'SEVOJNO'}
    TUBICI = {'name': 'TUBIĆI', 'id': '15109', 'safe name': 'TUBICI'}
    UZICI = {'name': 'UZIĆI', 'id': '15110', 'safe name': 'UZICI'}
    RASNA = {'name': 'RASNA', 'id': '15111', 'safe name': 'RASNA'}
    LESKOVICE = {'name': 'LESKOVICE', 'id': '15112', 'safe name': 'LESKOVICE'}
    GLUMAC = {'name': 'GLUMAC', 'id': '15113', 'safe name': 'GLUMAC'}
    ZLAKUSA = {'name': 'ZLAKUSA', 'id': '15114', 'safe name': 'ZLAKUSA'}
    OTANJ = {'name': 'OTANJ', 'id': '15116', 'safe name': 'OTANJ'}
    RACA = {'name': 'RAČA', 'id': '15118', 'safe name': 'RACA'}
    POZEGA = {'name': 'POŽEGA', 'id': '15150', 'safe name': 'POZEGA'}
    UZICE_TERETNA = {'name': 'UŽICE TERETNA', 'id': '15151', 'safe name': 'UZICE_TERETNA'}
    UZICE = {'name': 'UŽICE', 'id': '15153', 'safe name': 'UZICE'}
    BELA_REKA = {'name': 'BELA REKA', 'id': '15201', 'safe name': 'BELA_REKA'}
    BARAJEVO = {'name': 'BARAJEVO', 'id': '15203', 'safe name': 'BARAJEVO'}
    BARAJEVO_CENTAR = {'name': 'BARAJEVO CENTAR', 'id': '15204', 'safe name': 'BARAJEVO_CENTAR'}
    VELIKI_BORAK = {'name': 'VELIKI BORAK', 'id': '15205', 'safe name': 'VELIKI_BORAK'}
    LESKOVAC_KOLUBARSKI = {'name': 'LESKOVAC KOLUBARSKI', 'id': '15206', 'safe name': 'LESKOVAC_KOLUBARSKI'}
    STEPOJEVAC = {'name': 'STEPOJEVAC', 'id': '15207', 'safe name': 'STEPOJEVAC'}
    LAZAREVAC = {'name': 'LAZAREVAC', 'id': '15209', 'safe name': 'LAZAREVAC'}
    SLOVAC = {'name': 'SLOVAC', 'id': '15211', 'safe name': 'SLOVAC'}
    MLADJEVO = {'name': 'MLAĐEVO', 'id': '15212', 'safe name': 'MLADJEVO'}
    DIVCI = {'name': 'DIVCI', 'id': '15213', 'safe name': 'DIVCI'}
    IVERAK = {'name': 'IVERAK', 'id': '15215', 'safe name': 'IVERAK'}
    VREOCI = {'name': 'VREOCI', 'id': '15250', 'safe name': 'VREOCI'}
    VALJEVO = {'name': 'VALJEVO', 'id': '15251', 'safe name': 'VALJEVO'}
    LAJKOVAC = {'name': 'LAJKOVAC', 'id': '15260', 'safe name': 'LAJKOVAC'}
    RIPANJ = {'name': 'RIPANJ', 'id': '15402', 'safe name': 'RIPANJ'}
    KLENJE = {'name': 'KLENJE', 'id': '15403', 'safe name': 'KLENJE'}
    RIPANJ_TUNEL = {'name': 'RIPANJ TUNEL', 'id': '15404', 'safe name': 'RIPANJ_TUNEL'}
    RALJA = {'name': 'RALJA', 'id': '15405', 'safe name': 'RALJA'}
    SOPOT_KOSMAJSKI = {'name': 'SOPOT KOSMAJSKI', 'id': '15406', 'safe name': 'SOPOT_KOSMAJSKI'}
    VLASKO_POLJE = {'name': 'VLAŠKO POLJE', 'id': '15407', 'safe name': 'VLASKO_POLJE'}
    RIPANJ_KOLONIJA = {'name': 'RIPANJ KOLONIJA', 'id': '15408', 'safe name': 'RIPANJ_KOLONIJA'}
    MLADENOVAC = {'name': 'MLADENOVAC', 'id': '15460', 'safe name': 'MLADENOVAC'}
    RESNIK = {'name': 'RESNIK', 'id': '15501', 'safe name': 'RESNIK'}
    STAPARI = {'name': 'STAPARI', 'id': '15701', 'safe name': 'STAPARI'}
    SUSICA = {'name': 'SUŠICA', 'id': '15702', 'safe name': 'SUSICA'}
    BRANESCI = {'name': 'BRANEŠCI', 'id': '15703', 'safe name': 'BRANESCI'}
    ZLATIBOR = {'name': 'ZLATIBOR', 'id': '15704', 'safe name': 'ZLATIBOR'}
    RIBNICA_ZLATIBORSKA = {'name': 'RIBNICA ZLATIBORSKA', 'id': '15705', 'safe name': 'RIBNICA_ZLATIBORSKA'}
    JABLANICA = {'name': 'JABLANICA', 'id': '15706', 'safe name': 'JABLANICA'}
    STRPCI = {'name': 'ŠTRPCI', 'id': '15707', 'safe name': 'STRPCI'}
    PRIBOJ = {'name': 'PRIBOJ', 'id': '15708', 'safe name': 'PRIBOJ'}
    PRIBOJSKA_BANJA = {'name': 'PRIBOJSKA BANJA', 'id': '15709', 'safe name': 'PRIBOJSKA_BANJA'}
    BISTRICA_NA_LIMU = {'name': 'BISTRICA NA LIMU', 'id': '15710', 'safe name': 'BISTRICA_NA_LIMU'}
    PRIJEPOLJE = {'name': 'PRIJEPOLJE', 'id': '15711', 'safe name': 'PRIJEPOLJE'}
    PRIJEPOLJE_TERETNA = {'name': 'PRIJEPOLJE TERETNA', 'id': '15712', 'safe name': 'PRIJEPOLJE_TERETNA'}
    BRODAREVO = {'name': 'BRODAREVO', 'id': '15714', 'safe name': 'BRODAREVO'}
    RISTANOVICA_POLJE = {'name': 'RISTANOVIĆA POLJE', 'id': '15716', 'safe name': 'RISTANOVICA_POLJE'}
    TRIPKOVA = {'name': 'TRIPKOVA', 'id': '15717', 'safe name': 'TRIPKOVA'}
    DZUROVO = {'name': 'DŽUROVO', 'id': '15718', 'safe name': 'DZUROVO'}
    POLJICE = {'name': 'POLJICE', 'id': '15722', 'safe name': 'POLJICE'}
    ZEMUN_POLJE = {'name': 'ZEMUN POLJE', 'id': '16001', 'safe name': 'ZEMUN_POLJE'}
    ZEMUN = {'name': 'ZEMUN', 'id': '16002', 'safe name': 'ZEMUN'}
    NOVI_BEOGRAD = {'name': 'NOVI BEOGRAD', 'id': '16003', 'safe name': 'NOVI_BEOGRAD'}
    SEBES = {'name': 'SEBEŠ', 'id': '16006', 'safe name': 'SEBES'}
    OVCA = {'name': 'OVČA', 'id': '16007', 'safe name': 'OVCA'}
    TOSIN_BUNAR = {'name': 'TOŠIN BUNAR', 'id': '16012', 'safe name': 'TOSIN_BUNAR'}
    PANCEVACKI_MOST = {'name': 'PANČEVAČKI MOST', 'id': '16013', 'safe name': 'PANCEVACKI_MOST'}
    PANCEVO_STRELISTE = {'name': 'PANČEVO STRELIŠTE', 'id': '16014', 'safe name': 'PANCEVO_STRELISTE'}
    KRNJACA = {'name': 'KRNJAČA', 'id': '16015', 'safe name': 'KRNJACA'}
    KRNJACA_MOST_STA = {'name': 'KRNJAČA MOST STA', 'id': '16016', 'safe name': 'KRNJACA_MOST_STA'}
    BEOGRAD_CENTAR = {'name': 'BEOGRAD CENTAR', 'id': '16052', 'safe name': 'BEOGRAD_CENTAR'}
    KARADJORDJEV_PARK = {'name': 'KARAĐORĐEV PARK', 'id': '16053', 'safe name': 'KARADJORDJEV_PARK'}
    VUKOV_SPOMENIK = {'name': 'VUKOV SPOMENIK', 'id': '16054', 'safe name': 'VUKOV_SPOMENIK'}
    KIJEVO = {'name': 'KIJEVO', 'id': '16101', 'safe name': 'KIJEVO'}
    KNEZEVAC = {'name': 'KNEZEVAC', 'id': '16102', 'safe name': 'KNEZEVAC'}
    RAKOVICA = {'name': 'RAKOVICA', 'id': '16103', 'safe name': 'RAKOVICA'}
    BATAJNICA = {'name': 'BATAJNICA', 'id': '16204', 'safe name': 'BATAJNICA'}
    MAJUR_STAJ = {'name': 'MAJUR STAJ', 'id': '16300', 'safe name': 'MAJUR_STAJ'}
    PRNJAVOR_MACVANSKI = {'name': 'PRNJAVOR MAČVANSKI', 'id': '16305', 'safe name': 'PRNJAVOR_MACVANSKI'}
    LESNICA = {'name': 'LEŠNICA', 'id': '16307', 'safe name': 'LESNICA'}
    LOZNICA = {'name': 'LOZNICA', 'id': '16310', 'safe name': 'LOZNICA'}
    KOVILJACA = {'name': 'KOVILJAČA', 'id': '16312', 'safe name': 'KOVILJACA'}
    BRASINA = {'name': 'BRASINA', 'id': '16314', 'safe name': 'BRASINA'}
    DONJA_BORINA_STAJ = {'name': 'DONJA BORINA STAJ', 'id': '16315', 'safe name': 'DONJA_BORINA_STAJ'}
    ZVORNIK = {'name': 'ZVORNIK', 'id': '16317', 'safe name': 'ZVORNIK'}
    SABAC = {'name': 'ŠABAC', 'id': '16350', 'safe name': 'SABAC'}
    NOVA_PAZOVA = {'name': 'NOVA PAZOVA', 'id': '16501', 'safe name': 'NOVA_PAZOVA'}
    STARA_PAZOVA = {'name': 'STARA PAZOVA', 'id': '16503', 'safe name': 'STARA_PAZOVA'}
    GOLUBINCI = {'name': 'GOLUBINCI', 'id': '16505', 'safe name': 'GOLUBINCI'}
    PUTINCI = {'name': 'PUTINCI', 'id': '16506', 'safe name': 'PUTINCI'}
    KRALJEVCI_STAJ = {'name': 'KRALJEVCI STAJ', 'id': '16507', 'safe name': 'KRALJEVCI_STAJ'}
    SREMSKA_MITROVICA = {'name': 'SREMSKA MITROVICA', 'id': '16509', 'safe name': 'SREMSKA_MITROVICA'}
    MARTINCI = {'name': 'MARTINCI', 'id': '16511', 'safe name': 'MARTINCI'}
    KUKUJEVCI_ERDEVIK = {'name': 'KUKUJEVCI-ERDEVIK', 'id': '16513', 'safe name': 'KUKUJEVCI-ERDEVIK'}
    SID = {'name': 'ŠID', 'id': '16516', 'safe name': 'SID'}
    RUMA = {'name': 'RUMA', 'id': '16550', 'safe name': 'RUMA'}
    BUDJANOVCI = {'name': 'BUĐANOVCI', 'id': '16601', 'safe name': 'BUDJANOVCI'}
    NIKINCI = {'name': 'NIKINCI', 'id': '16602', 'safe name': 'NIKINCI'}
    PLATICEVO = {'name': 'PLATIĆEVO', 'id': '16603', 'safe name': 'PLATICEVO'}
    KLENAK = {'name': 'KLENAK', 'id': '16604', 'safe name': 'KLENAK'}
    INDJIJA = {'name': 'INĐIJA', 'id': '16801', 'safe name': 'INDJIJA'}
    BESKA = {'name': 'BEŠKA', 'id': '16802', 'safe name': 'BESKA'}
    SREMSKI_KARLOVCI = {'name': 'SREMSKI KARLOVCI', 'id': '16806', 'safe name': 'SREMSKI_KARLOVCI'}
    PETROVARADIN = {'name': 'PETROVARADIN', 'id': '16807', 'safe name': 'PETROVARADIN'}
    NOVI_SAD = {'name': 'NOVI SAD', 'id': '16808', 'safe name': 'NOVI_SAD'}
    NOVI_SAD_RANZIRNA = {'name': 'NOVI SAD RANŽIRNA', 'id': '16870', 'safe name': 'NOVI_SAD_RANZIRNA'}
    SZEGED = {'name': 'SZEGED', 'id': '17228', 'safe name': 'SZEGED'}
    SZENTMIHALYTELEK = {'name': 'SZENTMIHALYTELEK', 'id': '17665', 'safe name': 'SZENTMIHALYTELEK'}
    ROESZKE = {'name': 'ROESZKE', 'id': '17673', 'safe name': 'ROESZKE'}
    PANCEVO_VAROS = {'name': 'PANČEVO VAROŠ', 'id': '21001', 'safe name': 'PANCEVO_VAROS'}
    BANATSKO_NOVO_SELO = {'name': 'BANATSKO NOVO SELO', 'id': '21002', 'safe name': 'BANATSKO_NOVO_SELO'}
    VLADIMIROVAC = {'name': 'VLADIMIROVAC', 'id': '21003', 'safe name': 'VLADIMIROVAC'}
    ALIBUNAR = {'name': 'ALIBUNAR', 'id': '21004', 'safe name': 'ALIBUNAR'}
    BANATSKI_KARLOVAC = {'name': 'BANATSKI KARLOVAC', 'id': '21005', 'safe name': 'BANATSKI_KARLOVAC'}
    NIKOLINCI = {'name': 'NIKOLINCI', 'id': '21006', 'safe name': 'NIKOLINCI'}
    ULJMA = {'name': 'ULJMA', 'id': '21007', 'safe name': 'ULJMA'}
    VLAJKOVAC = {'name': 'VLAJKOVAC', 'id': '21008', 'safe name': 'VLAJKOVAC'}
    VRSAC = {'name': 'VRŠAC', 'id': '21009', 'safe name': 'VRSAC'}
    PANCEVO_VOJLOVICA = {'name': 'PANČEVO VOJLOVICA', 'id': '21101', 'safe name': 'PANCEVO_VOJLOVICA'}
    PANCEVO_GLAVNA = {'name': 'PANČEVO GLAVNA', 'id': '22001', 'safe name': 'PANCEVO_GLAVNA'}
    KACAREVO = {'name': 'KAČAREVO', 'id': '22003', 'safe name': 'KACAREVO'}
    CREPAJA = {'name': 'CREPAJA', 'id': '22004', 'safe name': 'CREPAJA'}
    DEBELJACA = {'name': 'DEBELJAČA', 'id': '22005', 'safe name': 'DEBELJACA'}
    KOVACICA = {'name': 'KOVAČICA', 'id': '22006', 'safe name': 'KOVACICA'}
    UZDIN = {'name': 'UZDIN', 'id': '22201', 'safe name': 'UZDIN'}
    TOMASEVAC = {'name': 'TOMAŠEVAC', 'id': '22202', 'safe name': 'TOMASEVAC'}
    ORLOVAT_STAJALISTE = {'name': 'ORLOVAT STAJALIŠTE', 'id': '22203', 'safe name': 'ORLOVAT_STAJALISTE'}
    LUKICEVO = {'name': 'LUKIĆEVO', 'id': '22204', 'safe name': 'LUKICEVO'}
    ZRENJANIN_FABRIKA = {'name': 'ZRENJANIN FABRIKA', 'id': '22501', 'safe name': 'ZRENJANIN_FABRIKA'}
    ELEMIR = {'name': 'ELEMIR', 'id': '22503', 'safe name': 'ELEMIR'}
    MELENCI = {'name': 'MELENCI', 'id': '22504', 'safe name': 'MELENCI'}
    KUMANE = {'name': 'KUMANE', 'id': '22505', 'safe name': 'KUMANE'}
    NOVI_BECEJ = {'name': 'NOVI BEČEJ', 'id': '22506', 'safe name': 'NOVI_BECEJ'}
    BANAT_MILOSEVO_POLJE = {'name': 'BANAT.MILOŠEVO POLJE', 'id': '22508', 'safe name': 'BANAT.MILOSEVO_POLJE'}
    BANATSKO_MILOSEVO = {'name': 'BANATSKO MILOŠEVO', 'id': '22509', 'safe name': 'BANATSKO_MILOSEVO'}
    ZRENJANIN = {'name': 'ZRENJANIN', 'id': '22550', 'safe name': 'ZRENJANIN'}
    BOCAR = {'name': 'BOČAR', 'id': '22601', 'safe name': 'BOCAR'}
    PADEJ = {'name': 'PADEJ', 'id': '22603', 'safe name': 'PADEJ'}
    OSTOJICEVO = {'name': 'OSTOJIĆEVO', 'id': '22604', 'safe name': 'OSTOJICEVO'}
    COKA = {'name': 'ČOKA', 'id': '22605', 'safe name': 'COKA'}
    KIKINDA = {'name': 'KIKINDA', 'id': '22850', 'safe name': 'KIKINDA'}
    KISAC = {'name': 'KISAČ', 'id': '23302', 'safe name': 'KISAC'}
    STEPANOVICEVO = {'name': 'STEPANOVIĆEVO', 'id': '23303', 'safe name': 'STEPANOVICEVO'}
    ZMAJEVO = {'name': 'ZMAJEVO', 'id': '23304', 'safe name': 'ZMAJEVO'}
    VRBAS_NOVA = {'name': 'VRBAS NOVA', 'id': '23305', 'safe name': 'VRBAS_NOVA'}
    LOVCENAC_MALI_IDJOS = {'name': 'Lovcenac Mali Idjos', 'id': '23307', 'safe name': 'LOVCENAC_MALI_IDJOS'}
    MALI_IDJOS_POLJE = {'name': 'MALI IĐOŠ POLJE', 'id': '23403', 'safe name': 'MALI_IDJOS_POLJE'}
    BACKA_TOPOLA = {'name': 'BAČKA TOPOLA', 'id': '23404', 'safe name': 'BACKA_TOPOLA'}
    ZEDNIK = {'name': 'ŽEDNIK', 'id': '23407', 'safe name': 'ZEDNIK'}
    NAUMOVICEVO = {'name': 'NAUMOVIĆEVO', 'id': '23409', 'safe name': 'NAUMOVICEVO'}
    SUBOTICA = {'name': 'SUBOTICA', 'id': '23450', 'safe name': 'SUBOTICA'}
    HORGOS = {'name': 'HORGOŠ', 'id': '23701', 'safe name': 'HORGOS'}
    BACKI_VINOGRADI = {'name': 'BAČKI VINOGRADI', 'id': '23702', 'safe name': 'BACKI_VINOGRADI'}
    HAJDUKOVO = {'name': 'HAJDUKOVO', 'id': '23703', 'safe name': 'HAJDUKOVO'}
    PALIC = {'name': 'PALIĆ', 'id': '23704', 'safe name': 'PALIC'}
    SUBOTICA_JAV_SKLADISTA = {'name': 'SUBOTICA JAV.SKLADIŠTA', 'id': '23706', 'safe name': 'SUBOTICA_JAV.SKLADISTA'}
    SENTA = {'name': 'SENTA', 'id': '23801', 'safe name': 'SENTA'}
    GORNJI_BREG = {'name': 'GORNJI BREG', 'id': '23802', 'safe name': 'GORNJI_BREG'}
    BOGARAS = {'name': 'BOGARAŠ', 'id': '23803', 'safe name': 'BOGARAS'}
    DOLINE = {'name': 'DOLINE', 'id': '23804', 'safe name': 'DOLINE'}
    OROM = {'name': 'OROM', 'id': '23805', 'safe name': 'OROM'}
    GABRIC = {'name': 'GABRIĆ', 'id': '23806', 'safe name': 'GABRIC'}
    GAJDOBRA = {'name': 'GAJDOBRA', 'id': '24001', 'safe name': 'GAJDOBRA'}
    FUTOG = {'name': 'FUTOG', 'id': '24003', 'safe name': 'FUTOG'}
    PETROVAC_GLOZAN = {'name': 'PETROVAC-GLOŽAN', 'id': '24004', 'safe name': 'PETROVAC-GLOZAN'}
    BACKI_MAGLIC = {'name': 'BAČKI MAGLIĆ', 'id': '24005', 'safe name': 'BACKI_MAGLIC'}
    SVETOZAR_MILETIC = {'name': 'SVETOZAR MILETIĆ', 'id': '24401', 'safe name': 'SVETOZAR_MILETIC'}
    ALEKSA_SANTIC = {'name': 'ALEKSA ŠANTIĆ', 'id': '24403', 'safe name': 'ALEKSA_SANTIC'}
    BAJMOK = {'name': 'BAJMOK', 'id': '24404', 'safe name': 'BAJMOK'}
    TAVANKUT = {'name': 'TAVANKUT', 'id': '24406', 'safe name': 'TAVANKUT'}
    LJUTOVO = {'name': 'LJUTOVO', 'id': '24407', 'safe name': 'LJUTOVO'}
    SEBESIC = {'name': 'ŠEBEŠIĆ', 'id': '24408', 'safe name': 'SEBESIC'}
    SUBOTICA_PREDGRADJE = {'name': 'SUBOTICA PREDGRAĐE', 'id': '24409', 'safe name': 'SUBOTICA_PREDGRADJE'}
    PARAGE = {'name': 'PARAGE', 'id': '25001', 'safe name': 'PARAGE'}
    RATKOVO = {'name': 'RATKOVO', 'id': '25002', 'safe name': 'RATKOVO'}
    ODZACI = {'name': 'ODŽACI', 'id': '25003', 'safe name': 'ODZACI'}
    ODZACI_KALVARIJA = {'name': 'ODŽACI KALVARIJA', 'id': '25401', 'safe name': 'ODZACI_KALVARIJA'}
    KARAVUKOVO = {'name': 'KARAVUKOVO', 'id': '25402', 'safe name': 'KARAVUKOVO'}
    BOGOJEVO_SELO = {'name': 'BOGOJEVO SELO', 'id': '25403', 'safe name': 'BOGOJEVO_SELO'}
    BOGOJEVO = {'name': 'BOGOJEVO', 'id': '25470', 'safe name': 'BOGOJEVO'}
    SONTA = {'name': 'SONTA', 'id': '25501', 'safe name': 'SONTA'}
    PRIGREVICA = {'name': 'PRIGREVICA', 'id': '25502', 'safe name': 'PRIGREVICA'}
    BUKOVACKI_SALASI = {'name': 'BUKOVAČKI SALAŠI', 'id': '25503', 'safe name': 'BUKOVACKI_SALASI'}
    SOMBOR = {'name': 'SOMBOR', 'id': '25550', 'safe name': 'SOMBOR'}
    PODGORICA = {'name': 'PODGORICA', 'id': '31001', 'safe name': 'PODGORICA'}
    GOLUBOVCI = {'name': 'GOLUBOVCI', 'id': '31002', 'safe name': 'GOLUBOVCI'}
    SUTOMORE = {'name': 'SUTOMORE', 'id': '31008', 'safe name': 'SUTOMORE'}
    BAR = {'name': 'BAR', 'id': '31080', 'safe name': 'BAR'}
    BIJELO_POLJE = {'name': 'BIJELO POLJE', 'id': '31302', 'safe name': 'BIJELO_POLJE'}
    MOJKOVAC = {'name': 'MOJKOVAC', 'id': '31305', 'safe name': 'MOJKOVAC'}
    KOLASIN = {'name': 'KOLAŠIN', 'id': '31307', 'safe name': 'KOLASIN'}

    def asJSON():
        return jsonDumps({member.name: member.value for member in Station})

class TrainDirection(Flag):
    INBOUND = auto()
    OUTBOUND = auto()

@dataclass
class Arrival:
    TrainNumber: int
    ArrivalTime: str
    DepartureTime: str
    Direction: TrainDirection
    Note: str
    IsLate: bool
    TrainType: TrainType

@dataclass
class TimeTable:
    LastUpdated: str
    Arrivals: list[Arrival]
    Station: Station

    def toJSON(self) -> str:
        return jsonDumps(self, cls=DataclassJSONEncoder)

class TrainApi:
    def getStations(self, search=""):
        res = requests.get(f"{API_BASE_URL}/stanica/?term={urllib.parse.quote(search)}")

        if res.status_code != 200:
            raise TrainException(f"Api error occured: {res.status_code}, {res.text}")

        stations_ = res.json()

        return list(map(lambda s: { \
            "name": s["naziv"], 
            "id": s["sifra"], 
            "safe name": s["naziv"].upper().replace(" ", "_").replace("Č", "C").replace("Ć", "C").replace("Š", "S").replace("Đ", "DJ").replace("Ž", "Z") 
        }, stations_))
    
    def getTimeTable(self, station: Station, date: str, directions: TrainDirection = TrainDirection.INBOUND | TrainDirection.OUTBOUND) -> TimeTable:
        arrivals = list()
    
        date = datetime.datetime.strftime(parse_date(date), "%d.%m.%Y")
        station_url = f"{WEB_BASE_URL}//stanicni/{urllib.parse.quote(station.value.get("safe name"))}/{station.value.get("id")}"

        for dir_ in directions:
            url = f"{station_url}/{date}/0000/{"dolazak" if dir_ == TrainDirection.INBOUND else "polazak"}/999/sr"

            res = requests.get(url)

            if res.status_code != 200:
                raise TrainException(f"Could not get timetable: {res.status_code}, {res.text}, url: {url}")

            #parse html
            html = BeautifulSoup(res.text, 'lxml')
            
            #get table from html
            table_rows = html.select("#rezultati > table > tr.tsmall")

            #get headers
            table_headers = list(map(lambda h: h.get_text(strip=True), table_rows[0].find_all("th")))[:-1]
            table_headers.append("Details")

            for row in table_rows[1:]:
                #get data from row
                data = list(map(lambda d: d.get_text(strip=True), row.select("td")))
            
                timetable_row = {}

                #go throught the headers
                for i in range(0, len(table_headers)):
                    if i >= len(data): #handle if no data for header
                        continue

                    if table_headers[i] == "Rang": #for rang, we get from image
                        try:
                            data[i] = row.select_one("td > img").attrs["title"]
                        except:
                            data[i] = "???"

                    timetable_row[table_headers[i]] = data[i]

                arrivals.append(Arrival(
                    TrainNumber=timetable_row["Broj voza"],
                    ArrivalTime=timetable_row["Vreme dolaska"],
                    DepartureTime=timetable_row["Vreme polaska"],
                    IsLate=len(timetable_row["Kasni"]) > 0,
                    Direction=dir_,
                    TrainType=TrainType.parse(timetable_row["Rang"]),
                    Note=timetable_row["Napomena"]
                ))

        return TimeTable(LastUpdated=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z%z"), Station=station, Arrivals=arrivals)
        