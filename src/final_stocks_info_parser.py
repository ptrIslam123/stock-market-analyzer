import logging
import re

from bs4 import BeautifulSoup
from stock_info import StockInfo

class FinalStocksInfoParser:
    def parse_stocks(self, page_content: str) -> list[StockInfo]:
        data = list()
        soup = BeautifulSoup(page_content, 'html.parser')
        table = soup.find('table', id='finfin-local-plugin-quote-table-table-table')

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
                        if name in self.__stocks_dict:
                            ticker = self.__stocks_dict[name]
                            last_price = self.__parse_price(row_data[1])
                            last_volume = self.__parse_volume(row_data[7])
                            stock_info = StockInfo(ticker=ticker, last_price=last_price, last_volume=last_volume)
                            data.append(stock_info)
                        else:
                            if name in self.__ignore_stocks_list == False:
                                logging.error(f"Could not find the company with name={name}")
        return data

    @staticmethod
    def __parse_price(price_str: str) -> float:
        # Удаляем символ валюты и заменяем запятую на точку
        if len(price_str) == 0:
            return 0
        else:
            return float(re.sub(r'[^\d,]', '', price_str).replace(',', '.'))

    @staticmethod
    def __parse_percent(percent_str) -> float:
        # Удаляем символ процента и заменяем запятую на точку
        if len(percent_str) == 0:
            return 0

        is_negative = percent_str.startswith('-')
        cleaned_str = re.sub(r'[^\d,]', '', percent_str)
        percent_value = float(cleaned_str.replace(',', '.'))
        if is_negative:
            percent_value = -percent_value

        return percent_value

    @staticmethod
    def __parse_volume(volume_str) -> int:
        # Удаляем пробелы и преобразуем в целое число
        if len(volume_str) == 0:
            return 0
        else:
            return int(re.sub(r'\s', '', volume_str))

    def get_stocks_dict(self):
        return self.__stocks_dict

    def __init__(self):
        self.__ignore_stocks_list = ["ВИ.ру", "Ванино-ао"]
        self.__stocks_dict = {
            # name : ticker
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
            "ГР Липецк": "LPOG",
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
            "ОВК ао": "UWGN",
            "Сегежа": "SGZH",
            "ИнтерРАОао": "IRAO",
            "AMNR ETF (АТОН – Накопительный в рублях)": "AMNR",
            "ЭсЭфАй ао": "SFIN",
            "iВУШХолднг": "VSEH",
            "СПБ Биржа": "SPBE",
            "ДВМП ао": "FESH",
            "Ванино-ао": "MTPV",
            "GLTR-гдр": "GLTR",
            "Яковлев-3": "IRKT",
            "Solidcore": "POLY",
            "Совкомбанк": "SVCB",
            "Астра ао": "ASTR",
            "ГТМ ао": "GTRK",
            "М.видео": "MVID",
            "Россети": "FEES",
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
            "iАвиастКао": "UNAC",
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
            "РСетиЛЭ-п": "LSNGP",
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
            "ЛЭСК ао": "LPSB",
            "РСетиМР ао": "MSRS",
            "TRUR ETF (БПИФ Т-Кап ВЕЧНЫЙ ПОРТФ РУБ)": "TRUR",
            "Таттел. ао": "TTLK",
            "РСетиСЗ ао": "MRKZ",
            "КрасОкт-ао": "KROT",
            "ЧЗПСН ао": "PRFN",
            "НКНХ ап": "NKNCP",
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
            "БСП ап": "BSPBP",
            "ЯТЭК ао": "YAKG",
            "iММЦБ ао": "MTSB",
            "ТГК-2 ап": "TGKBP",
            "РСетКубань": "KUBE",
            "ЭнергияРКК": "RKKE",
            "ГР Ставрпл": "STPL",
            "VEON": "VEON-RX",
            "AMNY ETF (АТОН - Накопительный в юанях)": "AMNY",
            "РоссЦентр": "MRKC",
            "OKEY-гдр": "OKEY",
            "Лензол. ап": "LNZLP",
            "ТНСэКубань": "KBSB",
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
            "ГР Воронеж": "VOGZ",
            "АстрЭнСб": "ASTP",
            "СтаврЭнСбп": "STSBP",
            "СтаврЭнСб": "STSB",
            "Синтез ап": "LIFE",
            "Куйбазот-п": "KAZTP",
            "ЮУНК ао": "UNKL",
            "TMOS ETF (БПИФ ТИНЬКОФФ ИНДЕКС МОСБИРЖИ)": "TMOS",
            "ГР Ярослвл": "YROG",
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
            "РОСИНТЕРао": "ROST",
            "Светофор п": "SVFOP",
            "ГАЗ ао": "GAZA",
            "ГазпрАвт-п": "GASP",
            "ЗаводДИОД": "ZDOD",
            "КрасОкт-1п": "KROTP",
            "ТНСэнРст": "RSTB",
            "КамчатЭ ап": "KCHEP",
            "ДонскЗР": "DZRD",
            "КузнецкийБ": "KUZB",
            "TBRU ETF (БПИФ Т-Капитал ОБЛИГАЦИИ)": "TBRU",
            "МордЭнСб": "MORS",
            "ТНСэнВор-п": "VRSBP",
            "Россети СК": "MRKK",
            "ОМЗ-ап": "OMZZP",
            "ГР Смленск": "SMLN",
            "ТНСэнМарЭл": "MELB",
            "Варьеган-п": "VRGNP",
            "Ижсталь2ао": "IZST",
            "ТНСэнЯр": "YRSB",
            "Ижсталь ап": "IZSTP",
            "СмоленНП-п": "SMNP",
            "Варьеган": "VRGN",
            "ПавлАвт ао": "PAVT",
            "КМЗ": "KMZ",
            "СаратЭн-ао": "SARE",
            "Ванино-ап": "VANI",
            "SCLI ETF (БПИФ Ликвидный)": "SCLI",
            "МагадЭн ао": "MAGE",
            "SBMX ETF (БПИФ Первая Топ Рос. акций)": "SBMX",
            "ТамбЭнСб-п": "TMSP",
            "ВолгЭнСб": "VENG",
            "ГР Тверь": "TVRS",
            "КоршГОК ао": "KOGK",
            "Сахэнер ао": "SAHE",
            "ДонскЗР п": "DZRDP",
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
            "ГАЗ ап": "GAZAP",
            "НЕФАЗ": "NEFZ",
            "Слав-ЯНОСп": "SLVNP",
            "ГР Уфа-ао": "UFAS",
            "НакопРез (ОПИФ Накопительный резерв)": "NRES",
            "ВолгаФ-ап": "VLGF",
            "КурганГКао": "KURG",
            "ОПИФ MM (ОПИФ МКБ Денежный рынок)": "MM",
            "SBFR ETF (БПИФ Первая Облигации флоатеры)": "SBFR",
            "TDIV ETF (Т-Капитал ДИВИДЕНДНЫЕ АКЦИИ)": "TDIV",
            "СаратЭн-ап": "SAMEP",
            "TLCB ETF (Т-КАПИТАЛ ВАЛЮТНЫЕ ОБЛИГАЦИИ)": "TLCB",
            "Мегион-ао": "MEGN",
            "БКСКапитал (ОПИФ БКС Капитал)": "BKSK",
            "ИНГРАД ао": "INGR",
            "ЧКПЗ ао": "CHKP",
            "ETF AKME (БПИФ Альфа Управляем Акции)": "AKME",
            "НИТЕЛ ао": "NITL",
            "РСТомск ап": "TORSP",
            "Химпром ап": "HMPR",
            "ИПИФМирИнв (ИПИФ Мировые инвестиции УКАтон)": "MIRI",
            "AKUP ETF (Альфа-Капитал Умный портфель)": "AKUP",
            "РСТомск ао": "TORS",
            "SBCS ETF (БПИФ Первая Консерватив смарт)": "SBCS",
            "ТамбЭнСб": "TMSB",
            "Удмуртнфт": "UDMN",
            "Якутскэн-п": "YKENP",
            "CNYM ETF (Ликвидность. Юань)": "CNYM",
            "Светофор": "SVFO",
            "ГР РостовП": "RTBGP",
            "OBLG ETF (БПИФ Российскиеоблигации УКВИМ)": "OBLG",
            "ТНСэнНН ао": "NNEN",
            "БЭСК ап": "BESK",
        }

        # test tickers table
        unique_tickers = set()
        for _, ticker in self.__stocks_dict.items():
            if ticker in unique_tickers:
                raise RuntimeError("Double defenition of the same tickers")
            else:
                unique_tickers.add(ticker)
