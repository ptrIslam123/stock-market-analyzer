import time
import re

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from stock_info import *
from global_configuration import *

ignore_stocks_list = ["ВИ.ру"]

stock_dict = {
    "Аэрофлот": "AFLT",
    "ВТБ ао": "VTBR",
    "ГАЗПРОМ ао": "GAZP",
    "ГМКНорНик": "GMKN",
    "ЛУКОЙЛ": "LKOH",
    "МТС-ао": "MTSS",
    "Магнит ао": "MGNT",
    "МосБиржа": "MOEX",
    "НЛМК ао": "NLMK",
    "Роснефть": "ROSN",
    "Ростел -ао": "RTKM",
    "РусГидро": "HYDR",
    "Сбербанк": "SBER",
    "СевСт-ао": "CHMF",
    "Сургнфгз": "SNGS",
    "ГР Липецк": "CHMK",
    "LQDT ETF (БПИФ Ликвидность УК ВИМ)": "LQDT",
    "Хэдхантер": "HEAD",
    "ТКСХолд ао": "TCSG",
    "ЯНДЕКС": "YDEX",
    "Новатэк ао": "NVTK",
    "Мечел ао": "MTLR",
    "OZON-адр": "OZON",
    "Полюс": "PLZL",
    "Татнфт 3ао": "TATN",
    "Газпрнефть": "SIBN",
    "ЕвроТранс": "EUTR",
    "Сургнфгз-п": "SNGSP",
    "Система ао": "AFKS",
    "МКПАО \"ВК\"": "VKCO",
    "Транснф ап": "TRNFP",
    "SBMM ETF (БПИФ Первая Сберегательный)": "SBMM",
    "ММК": "MAGN",
    "Сбербанк-п": "SBERP",
    "AKMM ETF (БПИФ Альфа Денежный рынок)": "AKMM",
    "АЛРОСА ао": "ALRS",
    "ПИК ао": "PIKK",
    "Совкомфлот": "FLOT",
    "Татнфт 3ап": "TATNP",
    "Самолет ао": "SMLT",
    "БСП ао": "BSPB",
    "ЮГК": "UGLD",
    "iПозитив": "POSI",
    "Мечел ап": "MTLRP",
    "ФосАгро ао": "PHOR",
    "РуссНфт ао": "RNFT",
    "РУСАЛ ао": "RUAL",
    "ТМК ао": "TRMK",
    "ОВК ао": "OGKB",
    "Сегежа": "SGZH",
    "ИнтерРАОао": "IRAO",
    "AMNR ETF (АТОН – Накопительный в рублях)": "AMNR",
    "ЭсЭфАй ао": "SFIN",
    "iВУШХолднг": "VSEH",
    "СПБ Биржа": "BSPB",
    "ДВМП ао": "FESH",
    "Ванино-ао": "VTBR",
    "GLTR-гдр": "GLTR",
    "Яковлев-3": "IRKT",
    "Solidcore": "POLY",
    "Совкомбанк": "SVCB",
    "Астра ао": "ASTR",
    "ГТМ ао": "GECO",
    "М.видео": "MVID",
    "Россети": "MRKP",
    "Селигдар": "SELG",
    "AGRO-гдр": "AGRO",
    "НМТП ао": "NMTP",
    "ЛСР ао": "LSRG",
    "Распадская": "RASP",
    "Ростел -ап": "RTKMP",
    "Башнефт ап": "BANEP",
    "iСофтлайн": "SOFL",
    "Европлан": "LEAS",
    "АшинскийМЗ": "AMEZ",
    "iАвиастКао": "VSMO",
    "Юнипро ао": "UPRO",
    "МКБ ао": "CBOM",
    "МТС Банк": "MBNK",
    "Белон ао": "BLNG",
    "iАРТГЕН ао": "ABIO",
    "Аренадата": "DATA",
    "ЭН+ГРУП ао": "ENPG",
    "Лента ао": "LENT",
    "MDMG-ао": "MDMG",
    "Башнефт ао": "BANE",
    "Займер ао": "ZAYM",
    "НоваБев ао": "BELU",
    "ИНАРКТИКА": "AQUA",
    "КАМАЗ": "KMAZ",
    "ТГК-14": "TGKN",
    "СОЛЛЕРС": "SVAV",
    "Ренессанс": "RENI",
    "iКаршеринг": "DELI",
    "Аптеки36и6": "APTK",
    "+МосЭнерго": "MSNG",
    "CIAN-адр": "CIAN",
    "TPAY ETF (Т-Капитал Пассивный Доход)": "TPAY",
    "РСетиЛЭ-п": "MRKP",
    "iQIWI": "QIWI",
    "МКПАО ЮМГ": "GEMC",
    "Русолово": "ROLO",
    "iДиасофт": "DIAS",
    "Акрон": "AKRN",
    "ГК РБК ао": "RBCM",
    "РСетиЦП ао": "MRKP",
    "ЭЛ5Энер ао": "ELFV",
    "ETLN-гдр": "ETLN",
    "ЧеркизГ-ао": "GCHE",
    "ВСМПО-АВСМ": "VSMO",
    "FIXP-гдр": "FIXP",
    "Росбанк ао": "ROSB",
    "ХЭНДЕРСОН": "HNFG",
    "Мостотрест": "MSTT",
    "ТГК-1": "TGKA",
    "ОргСинт ао": "KZOS",
"BCSD ETF (БПИФ БКС Денежный рынок)": "BCSD",
    "Россети Ур": "MRKU",
    "ПРОМОМЕД": "PRMD",
    "НКХП ао": "NKHP",
    "АбрауДюрсо": "ABRD",
    "ДетскийМир": "DSKY",
    "РСетиЛЭ": "LSNG",
    "iГЕНЕТИКО": "GECO",
    "iИВА": "IVAT",
    "ОГК-2 ао": "OGKB",
    "МГКЛ": "MGKL",
    "Лензолото": "LNZL",
    "СТГ": "STGZ",
    "ЛЭСК ао": "LSNG",
    "РСетиМР ао": "MRKP",
    "TRUR ETF (БПИФ Т-Кап ВЕЧНЫЙ ПОРТФ РУБ)": "TRUR",
    "Таттел. ао": "TTLK",
    "РСетиСЗ ао": "MRKZ",
    "КрасОкт-ао": "KROT",
    "ЧЗПСН ао": "PRFN",
    "НКНХ ап": "NKNC",
    "ТГК-2": "TGKB",
    "Куйбазот": "KAZT",
    "СКАИ-ао": "SKYC",
    "НКНХ ао": "NKNC",
    "Фармсинтез": "FARM",
    "Надметзвд": "NMTZ",
    "ТЗА ао": "TZA",
    "ПермьЭнСб": "PMSB",
    "РсетСиб ао": "MRKS",
    "ТНСэнВорон": "VRSB",
    "ЧМК ао": "CHMK",
    "Бамстрой": "BSTG",
    "МГТС-4ап": "MGTSP",
    "ОргСинт ап": "KZOSP",
    "Элемент": "ELTZ",
    "РсетВол ао": "MRKV",
    "TGLD ETF (БПИФ Т-Капитал ЗОЛОТО)": "TGLD",
    "ДЭК ао": "DVEC",
    "КалужскСК": "KLSB",
    "ПермьЭнС-п": "PMSBP",
    "iНаукаСвяз": "NSVZ",
    "УрКузница": "URKZ",
    "Авангрд-ао": "AVAN",
    "РоссЮг ао": "MRKY",
    "ГР Ростов": "RSTI",
    "РГС СК ао": "RGSS",
    "БСП ап": "BSPB",
    "ЯТЭК ао": "YAKG",
    "iММЦБ ао": "MTSB",
    "ТГК-2 ап": "TGKBP",
    "РСетКубань": "MRKK",
    "ЭнергияРКК": "RKKE",
    "ГР Ставрпл": "STPL",
    "VEON": "VEON-RX",
    "AMNY ETF (АТОН - Накопительный в юанях)": "AMNY",
    "РоссЦентр": "MRKC",
    "OKEY-гдр": "OKEY",
    "Лензол. ап": "LNZLP",
    "ТНСэКубань": "KRSB",
    "Телеграф": "CNTL",
    "Кристалл": "KLVZ",
    "БурЗолото": "BURN",
    "РязЭнСб": "RZSB",
    "Победит": "POTN",
    "ТНСэнРст-п": "RSTP",
    "РН-ЗапСиб": "RNZS",
    "СаратНПЗ-п": "KRKNP",
    "ИКРУСС-ИНВ": "IRUS",
    "Форвард Эн": "FWEN",
    "ВХЗ-ао": "VHZL",
    "iНПОНаука": "NPOF",
    "ГИТ ао": "GITL",
    "ГР Екб": "EKBZ",
    "ГР Воронеж": "VRSB",
    "АстрЭнСб": "ASTP",
    "СтаврЭнСбп": "STSB",
    "СтаврЭнСб": "STSB",
    "Синтез ап": "SGZH",
    "Куйбазот-п": "KAZTP",
    "ЮУНК ао": "UNKL",
    "TMOS ETF (БПИФ ТИНЬКОФФ ИНДЕКС МОСБИРЖИ)": "TMOS",
    "ГР Ярослвл": "YRSB",
    "ЮТэйр ао": "UTAR",
    "УралСиб ао": "URSB",
    "ЗИЛ ао": "ZILL",
    "ТНСэнрг ао": "TNSB",
    "КамчатЭ ао": "KCHE",
    "Левенгук": "LEVN",
    "ЕвроЭлтех": "EETL",
    "Синтз": "SINT",
    "Нижкамшина": "NIZM",
    "Арсагера": "ARSA",
    "АПРИ": "APRI",
    "ЗВЕЗДА ао": "ZVEZ",
    "EQMX ETF (БПИФ Индекс МосБиржи УК ВИМ)": "EQMX",
    "Телеграф-п": "CNTLP",
    "Якутскэнрг": "YKEN",
    "СамарЭн-ао": "SAME",
    "РОСИНТЕРао": "ROSN",
    "Светофор п": "SVFO",
    "ГАЗ ао": "GAZA",
    "ГазпрАвт-п": "GASP",
    "ЗаводДИОД": "ZDOD",
    "КрасОкт-1п": "KROT",
    "ТНСэнРст": "RSTB",
    "КамчатЭ ап": "KCHE",
    "ДонскЗР": "DZRD",
    "КузнецкийБ": "KUZB",
    "TBRU ETF (БПИФ Т-Капитал ОБЛИГАЦИИ)": "TBRU",
    "МордЭнСб": "MORS",
    "ТНСэнВор-п": "VRSBP",
    "Россети СК": "MRKS",
    "ОМЗ-ап": "OMZZP",
    "ГР Смленск": "SMLN",
    "ТНСэнМарЭл": "MELB",
    "Варьеган-п": "VRGN",
    "Ижсталь2ао": "IZST",
    "ТНСэнЯр": "YRSB",
    "Ижсталь ап": "IZST",
    "СмоленНП-п": "SMNP",
    "Варьеган": "VRGN",
    "ПавлАвт ао": "PAVT",
    "КМЗ": "KMZ",
    "СаратЭн-ао": "SAME",
    "Ванино-ап": "VANI",
    "SCLI ETF (БПИФ Ликвидный)": "SCLI",
    "МагадЭн ао": "MAGN",
    "SBMX ETF (БПИФ Первая Топ Рос. акций)": "SBMX",
    "ТамбЭнСб-п": "TMSP",
    "ВолгЭнСб": "VENG",
    "ГР Тверь": "TVRS",
    "КоршГОК ао": "KOGK",
    "Сахэнер ао": "SAHE",
    "ДонскЗР п": "DZRD",
    "GOLD ETF (БПИФ Золото.Биржевой УК ВИМ)": "GOLD",
    "ГР Калуга": "KLGA",
    "РДБанк ао": "RDBK",
    "ТКЗКК ап": "TKZK",
    "PSMM ETF (БПИФ РФИ ПСБ–Денежный рынок)": "PSMM",
    "Дорисс": "DORI",
    "Нлэ": "NLE",
    "Славн-ЯНОС": "SLVN",
    "ТНСэнЯр-п": "YRSBP",
    "МГТС-5ао": "MGTS",
    "ЦМТ ао": "CMT",
    "Красэсб ао": "KRSB",
    "AKGD ETF (БПИФ Альфа Капитал Золото)": "AKGD",
    "Красэсб ап": "KRSBP",
    "Мэсс": "MESS",
    "ГАЗ ап": "GAZP",
    "НЕФАЗ": "NEFZ",
    "Слав-ЯНОСп": "SLVN",
    "ГР Уфа-ао": "UFAS",
    "НакопРез (ОПИФ Накопительный резерв)": "NRES",
    "ВолгаФ-ап": "VLGF",
    "КурганГКао": "KURG",
    "ОПИФ MM (ОПИФ МКБ Денежный рынок)": "MM",
    "SBFR ETF (БПИФ Первая Облигации флоатеры)": "SBFR",
    "TDIV ETF (Т-Капитал ДИВИДЕНДНЫЕ АКЦИИ)": "TDIV",
    "СаратЭн-ап": "SAME",
    "TLCB ETF (Т-КАПИТАЛ ВАЛЮТНЫЕ ОБЛИГАЦИИ)": "TLCB",
    "Мегион-ао": "MEGN",
    "БКСКапитал (ОПИФ БКС Капитал)": "BKSK",
    "ИНГРАД ао": "INGR",
    "ЧКПЗ ао": "CHKP",
    "ETF AKME (БПИФ Альфа Управляем Акции)": "AKME",
    "НИТЕЛ ао": "NITL",
    "РСТомск ап": "RTKM",
    "Химпром ап": "HMPR",
    "ИПИФМирИнв (ИПИФ Мировые инвестиции УКАтон)": "MIRI",
    "AKUP ETF (Альфа-Капитал Умный портфель)": "AKUP",
    "РСТомск ао": "RTKM",
    "SBCS ETF (БПИФ Первая Консерватив смарт)": "SBCS",
    "ТамбЭнСб": "TMSB",
    "Удмуртнфт": "UDMN",
    "Якутскэн-п": "YKEN",
    "CNYM ETF (Ликвидность. Юань)": "CNYM",
    "Светофор": "SVFO",
    "ГР РостовП": "RSTP",
    "OBLG ETF (БПИФ Российскиеоблигации УКВИМ)": "OBLG",
    "ТНСэнНН ао": "NNEN",
    "БЭСК ап": "BESK",
}

def parse_price(price_str: str) -> float:
    # Удаляем символ валюты и заменяем запятую на точку
    if len(price_str) == 0:
        return 0
    else:
        return float(re.sub(r'[^\d,]', '', price_str).replace(',', '.'))

def parse_percent(percent_str) -> float:
    # Удаляем символ процента и заменяем запятую на точку
    if len(percent_str) == 0:
        return 0

    is_negative = percent_str.startswith('-')
    cleaned_str = re.sub(r'[^\d,]', '', percent_str)
    percent_value = float(cleaned_str.replace(',', '.'))
    if is_negative:
        percent_value = -percent_value

    return percent_value

def parse_volume(volume_str) -> int:
    # Удаляем пробелы и преобразуем в целое число
    if len(volume_str) == 0:
        return 0
    else:
        return int(re.sub(r'\s', '', volume_str))

def parse_info(page_content: str):
    soup = BeautifulSoup(page_content, 'html.parser')
    table = soup.find('table', id='finfin-local-plugin-quote-table-table-table')

    data = list()
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all(['td', 'th']):
            row_data.append(cell.get_text(strip=True))

        if len(row_data) == 9:
            if all(item == "" for item in row_data[1:]):
                pass
            else:
                name = row_data[0]
                if name != str("Инструмент"):
                    if name in stock_dict:
                        ticker = stock_dict[name]
                        last_price = parse_price(row_data[1])
                        price_change_percent = parse_percent(row_data[2])
                        open_price = parse_price(row_data[3])
                        close_price = parse_price(row_data[6])
                        volume = parse_volume(row_data[7])
                        update_time = row_data[8]
                        stock_info = StockInfo(name=name, ticker=ticker,
                                               last_price=last_price, price_change_percent=price_change_percent,
                                               open_price=open_price, close_price=close_price, volume=volume,
                                               update_time=update_time)
                        data.append(stock_info)
                    else:
                        if name in ignore_stocks_list == False:
                            print(f"Could not find the company with name={name}")
    return data

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL)

    while True:
        try:
            page.get_by_role("button", name="Показать ещё").click(timeout=7000)
        except:
            break

    conn = sqlite3.connect(INTRADAY_STOCK_MARKET_INFO_TABLE_PATH)
    cursor = conn.cursor()

    while True:
        stocks_info_list = parse_info(page.content())
        if len(stocks_info_list) == 0:
            continue
        else:
            for stock_info in stocks_info_list:
                stock_info.create_table(cursor)
                stock_info.insert(cursor, conn)
            time.sleep(10)

    # ---------------------
    context.close()
    browser.close()

def main():
    with sync_playwright() as playwright:
        run(playwright)

if __name__ == "__main__":
    main()