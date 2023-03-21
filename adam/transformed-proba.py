import datetime
import socket
import requests
import logging
from datetime import datetime
import pytz

from ..kisegito import kisegito, idoszamitas, email_kuldo

logger = logging.getLogger('alaplogger')


def ryuphi_api_manager(tulajdonos_adatok):
    """
        :param tulajdonso_adatok:
        :return: egy dictionary, ami egy bolygó és egy ház komponenst tartalmaz
        - Ezek az alapvető adatok egy képlet felrejzolásához
    """
    logger.debug("Ryuphi API használata")
    kinyert_adatok = init_api(tulajdonos_adatok)
    # print(get_bolygok(kinyert_adatok))
    return {"bolygok": get_bolygok(kinyert_adatok), "hazak": get_hazak(kinyert_adatok)}


def char2(char):
    """Az 1 jegyű számokat két jegyűvé teszi, kipótolva egy 0-val az elejét """
    if len(str(char)) == 1:
        return "0" + str(char)
    return char

class RyuphiAPINemElerheto(Exception):
    """Nem lehet Képletet létrehozni, mert nincs elindítva az ehhez szükséges API"""
    pass

import platform
def ryuphi_adat_kinyeres(datumido_teljes_str, szelesseg, hosszusag):
    """
    Portok kezelése
    Melyik port nyitott - ellenőrzés
    :return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_talalat = sock.connect_ex(('127.0.0.1', 3000))

    if port_talalat == 0:
        logger.debug("Port is open : 3000 --> Belső API (gyors)")
        url = f'''
                  http://127.0.0.1:3000/horoscope?time={datumido_teljes_str}%2B00:00&latitude={szelesseg}&longitude={hosszusag}
                  '''
        adat = requests.get(url)
    else:
        logger.error("Nincs elindítva a Ryuphi API")
        email_kuldo.email_kuldes(f"Nincs elindítva a Ryuphi API ({platform.system()}{platform.release()})")
        raise RyuphiAPINemElerheto

    sock.close()

    return adat


def init_api(tul_adatok):
    """
    :param tul_adatok:
    :return: json ami tartalmazza a bolygó Jegyben és ház Jegyben adatokat
    """
    logger.debug("RYUPHI API INIT")
    start = datetime.now() # stopper indítása

    szelesseg, hosszusag = kisegito.varos_poz(helyisegnev=str(tul_adatok.hely))  # varos alapjan szél/hossz
    idozona = idoszamitas.idozona(szelesseg, hosszusag)  # idozona neve

    # GMT idő kiszámítása
    local = pytz.timezone(idozona)
    helyi_ido_datetime = datetime.strptime(f"{tul_adatok.ev}-{tul_adatok.honap}-{tul_adatok.napszam} "
                                           f"{tul_adatok.ora}:{tul_adatok.perc}:{tul_adatok.mp}", "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(helyi_ido_datetime, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    logger.debug(f"GMT idő: {utc_dt=}")

    datumido_teljes_str = f'{char2(utc_dt.year)}-{char2(utc_dt.month)}-{char2(utc_dt.day)}T' \
                          f'{char2(utc_dt.hour)}:{char2(utc_dt.minute)}:{char2(utc_dt.second)}'

    adat = ryuphi_adat_kinyeres(datumido_teljes_str, szelesseg, hosszusag)

    logger.debug(f"RYUPHI API Futásidő: {datetime.now() - start}")

    # egyéb adatok mentése
    tul_adatok.egyeb_adat["gmt_szulido"] = f'{char2(utc_dt.year)}.{char2(utc_dt.month)}.{char2(utc_dt.day)}. ' \
                                    f'{char2(utc_dt.hour)}:{char2(utc_dt.minute)}:{char2(utc_dt.second)}'
    tul_adatok.egyeb_adat["szelesseg"] = str(szelesseg)
    tul_adatok.egyeb_adat["hosszusag"] = str(hosszusag)
    print(adat)
    return adat.json()


def get_bolygok(chart:dict):
    """
    :param chart: dict
    :return: dict
    """
    bolygok = dict()

    bolygo_objektumok = chart["data"]["astros"]
    for key, value in bolygo_objektumok.items():
        if key == "chiron": # ezekre az adatokra már nincs szükség
            break
        # NINCS SZÜKSÉG KORRIGÁLÁSRA mert tizedestörtben ó
        # fokszam = float()
        # tizedesresz = (fokszam-int(fokszam))/10*6
        # korrigalt_fokszam = int(fokszam) + tizedesresz
        bolygok[kisegito.bolygo_to_hun(key)] = {
            "jegy": kisegito.jegy_num_to_hun(str(value["sign"])),
            "fokszam": float(get_fokszam(value["position"])),
            "retográd": value["retrograde"],
            "gyorsaság": value["speed"]
        }
    return bolygok


def get_fokszam(position):
    """
        Tizedes törtben ad vissza egy stringet
        Pl: '26.82613423'
    """
    return str(float(position["longitude"]) % 30)


def get_hazak(chart:dict):
    """
    :param chart: ryuphi chart json, alap bolygok, alap hazak
    :return:
    """
    hazak = dict()
    hazakiter = chart["data"]["houses"]
    for i, value in enumerate(hazakiter, 1):
        hazak[i] = {"jegy": kisegito.jegy_num_to_hun(str(value["sign"])),
                    "fokszam": get_fokszam(value["position"])}
    return hazak
