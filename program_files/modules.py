"""Файл со всеми программными функциями"""

import re
import math
from shapely.geometry import Point
from collections import defaultdict
from itertools import groupby
from importlib.machinery import SourceFileLoader

path = '../config.py'
module_name = 'config.py'
loader = SourceFileLoader(module_name, path)
config = loader.load_module()


# Поиск всех точек в файле ARINC
def get_points(list):
    for i in range(len(list)):
        line = list[i]
        pat1 = re.compile(r'^(SEEUP ).+')
        pat2 = re.compile(r'^(TEEUD).+')
        pat3 = re.compile(r'^(SPACP ).+')
        pat4 = re.compile(r'^(SEEUU).+')
        pat5 = re.compile(r'^(SEEUP).+')
        pat6 = re.compile(r'^(SEEUP UH).+')
        pat7 = re.compile(r'(?=[^0-9]{5})(?:.+)')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        s4 = pat4.search(line)
        s5 = pat5.search(line)
        s6 = pat6.search(line)
        name = line[13:18]
        s7 = pat7.search(name)
        if len(line) >= 41:
            if line[32] == 'N' and line[41] == 'E' and not s1 \
                    and not s2 and not s3 and not s4 and not s5:
                yield line
            if line[32] == 'N' and line[41] == 'E' and s6 and s7:
                pat8 = re.compile(r'\s|\S+')
                s8 = pat8.search(name)
                point = s8.group()
                if len(point) == 5:
                    yield line


"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""


def get_data(file):
    for i in range(len(file)):
        line = file[i]
        name = line[13:18]
        coord = line[32:51]
        N = line[32]
        E = line[41]
        pat = re.compile(r'\s|\S+')
        s = pat.search(name)
        ind = line[19:21]
        pat2 = re.compile(r'[0-9]+')
        s2 = pat2.search(name)
        if s and N == 'N' and E == 'E' and coord != 'N48314100E135111700' and not s2:
            point = s.group()
            if len(point) > 1:
                yield point, coord, ind


# Получение координат точек для дальнешего сравнения с базой
def data(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        lat = line[1][5:7]
        lon = line[1][15:17]
        yield name, lat, lon


# Полигон для Синтеза
poly = config.poly_sintez


# Сравнение точек из файла ARINC с зоной полигона для СИНТЕЗА
def inside(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        lat = lat * math.pi / 180
        lon = lon * math.pi / 180
        p = Point(lat, lon)
        if poly.contains(p):
            yield line


poly2 = config.poly_radar


# Сравнение точек из файла ARINC с зоной полигона для локатора
def inside_radar(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        p = Point(lon, lat)
        if poly2.contains(p):
            yield line


poly3 = config.poly_kor


# Сравнение точек из файла ARINC с зоной полигона для КОРИНФ
def inside_kor(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        p = Point(lon, lat)
        if poly3.contains(p):
            yield line


# Получение имен точек
def names(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        yield name


# Выбираем только уникальные названия
def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    for x in unique_list:
        yield x


# Нахождение дубликатов точек ARINC, которые попали в полигон
def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    yield ((key, locs) for key, locs in tally.items()
           if len(locs) > 1)


# Нахождение индексов дубликатов
def sep(dup):
    for key in dup:
        index = dup[key]
        yield index


def sep2(list, indexes):
    for item in indexes:
        line = list[item]
        yield line


# Преобразуем спиок в строки
def listTosring(arinc_duplicates):
    for i in range(len(arinc_duplicates)):
        line = arinc_duplicates[i]
        str1 = " "
        yield str1.join(line)


# Преобразуем спиок в строки
def listTosring2(list1):
    for i in range(len(list1)):
        line = list1[i]
        str1 = ", "
        yield str1.join(line)


# Заполняем файл POINTS_W.sld
def filling1(list, type):
    for i in range(len(list)):
        line = list[i]
        point = line[0]
        coord = line[1]
        if len(point) == 3:
            str1 = 'S: "6" <R4> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str1, str2
        if len(point) == 2:
            str1 = 'S: "1" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            str3 = 'S: "9" <R3> ' + coord
            yield str1, str2, str3, str2
        if len(point) != 2 and len(point) != 3 and point not in type:
            str1 = 'S: "1" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str1, str2
        if len(point) != 2 and len(point) != 3 and point in type:
            str1 = 'S: "2" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str1, str2


def filling1_1(lst, type):
    for i in range(len(lst)):
        line = lst[i]
        point = line[0]
        coord = line[1]
        if len(point) == 3:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "6" <R4> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str0, str1, str2
        if len(point) == 2:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "1" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            str3 = 'S: "9" <R3> ' + coord
            yield str0, str1, str2, str0, str3, str2
        if len(point) != 2 and len(point) != 3 and point not in type:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "1" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str0, str1, str2
        if len(point) != 2 and len(point) != 3 and point in type:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "2" <R1> ' + coord
            str2 = 'T: <R2> ' + coord + ' / ' + point + ' / '
            yield str0, str1, str2


def filling2(list):
    for i in range(len(list)):
        line = list[i]
        point = line[0]
        coord = line[1]
        str0 = 'SD: 0.0, 0.0'
        str1 = 'S: "9" <R1, BLACK> ' + coord
        str2 = 'T: <BLACK, R1> ' + coord + ' / ' + point + ' / '
        yield str0, str1, str2


def filling2_1(lst):
    for i in range(len(lst)):
        line = lst[i]
        point = line[0]
        coord = line[1]
        str0 = 'SD: 0.0, -1.0'
        str1 = 'S: "9" <R1, BLACK> ' + coord
        str2 = 'T: <BLACK, R1> ' + coord + ' / ' + point + ' / '
        yield str0, str1, str2


# Нахождение трасс в документе ARINC
def get_routes(file):
    for i in range(len(file)):
        line = file[i]
        pat1 = re.compile(r'^(SEEUER ).+')
        pat2 = re.compile(r'^(SPACER ).+')
        pat3 = re.compile(r'^(SCANER ).+')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        if s1:
            points = s1.group()
            yield points
        if s2:
            points = s2.group()
            yield points
        if s3:
            points = s3.group()
            yield points


# Функция сравнения
def find(new, old):
    for element in new:
        if element in old:
            yield element


# Сравнение совпавших по имени точек по координатам
def compare(a_doubles, b_doubles):
    for element in a_doubles:
        if element not in b_doubles:
            yield element


# Считаем трассы, где точек больше двух
def count_list(list1):
    for i in range(len(list1)):
        line = list1[i]
        len1 = len(line)
        if len1 > 1:
            yield line


# Установка порядковых номеров точек на маршруте
def counter_of_points_arinc(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i, each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(i)


# Пересчитываем градусы в радианы
def gradus(list1):
    for i in range(len(list1)):
        line = list1[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        mili_lat = int(line[1][7:9])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600 + mili_lat / 216000
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        mili_lon = int(line[1][17:19])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600 + mili_lon / 216000
        yield line[0], lat, lon


# Заполнение файла с маршрутами
def fill_routes(list):
    for i in range(len(list)):
        line = list[i]
        route = line[0]
        points = line[1]
        str1 = ", "
        points = str1.join(points)
        info = "L: " + "*" + route + "* " + points
        yield info


# Создание списка с десигнаторов
def make_desw(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
        first = 'SA: ' + sa
        third = 'T: <* BLACK * GREEN, R1> ' + coord + ' / ' + route + ' /'
        if a < 90:
            b = a * (math.pi / 180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a - 180) * (math.pi / 180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (180 - a) * (math.pi / 180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (360 - a) * (math.pi / 180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third


# Разбиваем на части
def chunks(lst, n):
    for q in range(len(lst)):
        line = lst[q]
        for i in range(0, len(line), n):
            yield line[i:i + n]


# Проверяем на наложение
def only_coords(lst):
    for i in range(len(lst)):
        line = lst[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        p = Point(lat, lon)
        yield line[0], p, line[2], lat, lon, line[1]


def check(output, sec):
    for i in range(len(output)):
        line = output[i]
        sec1 = sec / 3600
        poly = line[0].buffer(sec1)
        point = line[1]
        if poly.contains(point):
            yield line[2], line[3], line[4], line[5], line[6]
            yield line[7], line[8], line[9], line[10], line[11]


def get_same(lst1, lst2):
    for i in range(len(lst2)):
        line2 = lst2[i]
        name2 = line2[0]
        ind2 = line2[1]
        for q in range(len(lst1)):
            line = lst1[q]
            name = line[0]
            ind = line[2]
            if name == name2 and ind == ind2:
                yield line


def connecting(chained_minutes, zon):
    for i in range(len(chained_minutes)):
        line = chained_minutes[i]
        for q in range(len(zon)):
            if zon[q] == line[0]:
                yield line


def for_log_points(non_common, inside_points):
    for i in range(len(non_common)):
        point = non_common[i]
        for q in range(len(inside_points)):
            line = inside_points[q]
            point2 = line[0]
            if point == point2:
                yield line


def compare_new_points_and_routes(filtred_routes_num, test):
    for i in range(len(filtred_routes_num)):
        line = filtred_routes_num[i]
        point = line[1]
        ind = line[2]
        for q in range(len(test)):
            line2 = test[q]
            point2 = line2[0]
            ind2 = line2[2]
            if point == point2 and ind == ind2:
                yield line[0], line[1], line2[1], line[3]


def del_make_desw2(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        for q in range(len(list2)):
            line2 = list2[q]
            route = line[0]
            route2 = line2[0]
            sa = str(round(line[3], 1))
            coord = line[1]
            a = line[2]
            first = 'SA: ' + sa
            third = 'T: <* BLACK * GREEN, R1> ' + coord + ' / ' + route + '-' + route2 + ' /'
            if a < 90:
                b = a * (math.pi / 180)
                dx = str(round(math.cos(b) * (-0.2), 1))
                dy = str(round(math.sin(b) * (0.2), 1))
                second = 'SD: ' + dx + ', ' + dy
                # second = 'SD: '+ dx', 0.0'
                # second = 'SD: 0.0, 0.0'
                yield first
                yield second
                yield third
            if 180 < a < 270:
                b = (a - 180) * (math.pi / 180)
                dx = str(round(math.cos(b) * (-0.2), 1))
                dy = str(round(math.sin(b) * (0.2), 1))
                second = 'SD: ' + dx + ', ' + dy
                # second = 'SD: 0.0, 0.0'
                yield first
                yield second
                yield third
            if 90 < a < 180:
                b = (180 - a) * (math.pi / 180)
                dx = str(round(math.cos(b) * (0.2), 1))
                dy = str(round(math.sin(b) * (0.2), 1))
                second = 'SD: ' + dx + ', ' + dy
                # second = 'SD: 0.0, 0.0'
                yield first
                yield second
                yield third
            if 270 < a < 360:
                b = (360 - a) * (math.pi / 180)
                dx = str(round(math.cos(b) * (0.2), 1))
                dy = str(round(math.sin(b) * (0.2), 1))
                second = 'SD: ' + dx + ', ' + dy
                # second = 'SD: 0.0, 0.0'
                yield first
                yield second
                yield third


def make_list(lst):
    for x in lst:
        new = x.split(',')
        yield new


def delete_quotes(lst):
    pat = re.compile(r'[^"\']+')
    for i in range(len(lst)):
        line = lst[i]
        new_line = []
        for q in range(len(line)):
            elem = line[q]
            s = pat.search(elem)
            if s:
                new = s.group()
                new_line.append(new)
            else:
                new_line.append(elem)
        yield new_line


def create_quotes(lst):
    for x in lst:
        new = "'" + x + "'"
        yield new


# Отбор точек на кириллице из базы данных
def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


# Отбор точек на на латинице из базы данных
def has_latin(text):
    return bool(re.search('[A-Z]', text))


# Перерасчет координат точек из документа аринк в прямоугольной системе координат
def transform_arinc(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        hab_lat = 48 + 31 / 60 + 41 / 3600
        hab_lon = 135 + 11 / 60 + 17 / 3600
        lat1 = hab_lat * math.pi / 180
        lon1 = hab_lon * math.pi / 180
        lat2 = lat * math.pi / 180
        lon2 = lon * math.pi / 180
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
        x = sl1 * sl2 + cl1 * cl2 * cdelta
        ad = math.atan2(y, x)
        dist = ad * rad
        x = (cl1 * sl2) - (sl1 * cl2 * cdelta)
        y = sdelta * cl2
        z = math.degrees(math.atan(-y / x))
        if (x < 0):
            z = z + 180
        z2 = (z + 180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2 * math.pi) * math.floor((z2 / (2 * math.pi))))
        angledeg = (anglerad2 * 180) / math.pi
        x = round(((math.sin(anglerad2) * dist) / 1000), 3)
        y = round(((math.cos(anglerad2) * dist) / 1000), 3)
        shir = line[1][1:7]
        shir = shir + 'N'
        dolg = line[1][10:17]
        dolg = dolg + 'E'
        if x > 1000 and -1000 < y < 1000:
            k = x / 250
            x = round(x + k, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x < -1000 and -1000 < y < 1000:
            k = x / 250
            x = round(x + k, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x > 1000 and y > 1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x < -1000 and y > 1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x > 1000 and y < -1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x < -1000 and y < -1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if -1000 < x < 1000:
            yield line[0], shir, dolg, x, y, line[2]


# Сравнение совпаших точек на латинице
def compare_common_points(eng_common_points, points_base):
    eng_common_points_base = []
    for x in points_base:
        pat_space = re.compile(r'[^\s]+')
        pat_search = pat_space.search(x[0])
        without_space = pat_search.group()
        if without_space in eng_common_points:
            eng_common_points_base.append(x)
    return eng_common_points_base


def compare_common_arinc(arinc_transformed, eng_common_points):
    eng_common_points_arinc = []
    for x in arinc_transformed:
        if x[0] in eng_common_points:
            eng_common_points_arinc.append(x)
    return eng_common_points_arinc


# Нахождение совпаших точек, у которых разница в координатах более 10 сек
def compare_coordinates(arinc, base):
    for i in range(len(arinc)):
        if len(base[i][1]) == 7 and len(base[i][2]) == 8:
            lat_ar = int(arinc[i][1][0:6])
            lon_ar = int(arinc[i][2][0:7])
            lat_base = int(base[i][1][0:6])
            lon_base = int(base[i][2][0:7])
            if abs(lat_ar - lat_base) > 10 or abs(lon_ar - lon_base) > 10:
                yield base[i], arinc[i]
        else:
            yield base[i], arinc[i]


def update_query(lst):
    for i in range(len(lst)):
        line = lst[i]
        queryA = "UPDATE point set PN_NAME = '%s', PN_LAT = '%s', PN_LON = '%s', PN_X = %s, PN_Y = %s, PN_FNAME = %s, PN_NUM = %s, P_RP = %s, P_ACT = %s, P_STATE = %s, P_FIR = %s, P_TMA = %s, P_AOR = %s, P_SECTOR = %s, P_ZONE = %s, PN_CAPTION = '%s' WHERE PN_NAME = '%s';" % (
            line[0][0], line[1][1], line[1][2], line[1][3], line[1][4], line[0][5], line[0][6], line[0][7], line[0][8],
            line[0][9], line[0][10], line[0][11], line[0][12], line[0][13], line[0][14], line[0][15], line[0][0])
        queryB = "UPDATE point_mag set PN_NAME = '%s', PN_LAT = '%s', PN_LON = '%s', PN_X = %s, PN_Y = %s, PN_FNAME = %s, PN_NUM = %s, P_RP = %s, P_ACT = %s, P_STATE = %s, P_FIR = %s, P_TMA = %s, P_AOR = %s, P_SECTOR = %s, P_ZONE = %s, PN_CAPTION = '%s' WHERE PN_NAME = '%s';" % (
            line[0][0], line[1][1], line[1][2], line[1][3], line[1][4], line[0][5], line[0][6], line[0][7], line[0][8],
            line[0][9], line[0][10], line[0][11], line[0][12], line[0][13], line[0][14], line[0][15], line[0][0])
        yield queryA
        yield queryB


def query_03_add_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        query = "('%s', '%s', '%s', %s, %s, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL ) \n" % (
            line[0], line[1], line[2], str(line[3]), str(line[4]))
        yield query


# ______________________АНАЛИЗ ТРАСС_______________________________________

def get_route_info(list1_r):
    for i in range(len(list1_r)):
        line = list1_r[i]
        name = line[13:18]
        point = line[29:34]
        number = int(line[26:28])
        pat = re.compile(r'[^\s]+')
        s = pat.search(name)
        s2 = pat.search(point)
        name = s.group()
        point = s2.group()
        ind = line[34:36]
        min = line[83:88]
        max = line[93:98]
        yield name, point, ind, number, min, max


# Получаем список с трассами, которые лежат в зоне ответсвенности из ARINC
def select_routes(routes, inside_points):
    for i in range(len(routes)):
        line = routes[i]
        route = line[0]
        point = line[1]
        ind = line[2]
        for q in range(len(inside_points)):
            line2 = inside_points[q]
            point2 = line2[0]
            ind2 = line2[2]
            coord = line2[1]
            if point == point2 and ind == ind2:
                yield route, point, ind, coord, line[3], line[4], line[5]


def select_routes_lines(routes, inside_points):
    for i in range(len(routes)):
        line = routes[i]
        route = line[13:18]
        point = line[29:34]
        ind = line[34:36]
        pat = re.compile(r'[^\s]+')
        s = pat.search(route)
        s2 = pat.search(point)
        route = s.group()
        point = s2.group()
        for q in range(len(inside_points)):
            line2 = inside_points[q]
            point2 = line2[0]
            ind2 = line2[2]
            coord = line2[1]
            if point == point2 and ind == ind2:
                yield line


def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i, each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]), "{}".format(i), "{}".format(
                each[3]), "{}".format(each[5]), "{}".format(each[6]), "{}".format(each[4])


# Формируем слой с точками, которые участвуют в трассах (ничего лишнего)
def only_in_trass(more):
    only_in_trass_points = []
    for x in more:
        new = []
        new.append(x[1])
        new.append(x[4])
        new.append(x[2])
        new = tuple(new)
        only_in_trass_points.append(new)
    return only_in_trass_points


def add_quotes(lst):
    for i in range(len(lst)):
        line = lst[i]
        new = []
        for x in line:
            if x != 'NULL' and x != "''":
                new_x = "'" + x + "'"
                new.append(new_x)
            if x == "''":
                new_x = 'NULL'
                new.append(new_x)
            if x == 'NULL':
                new.append(x)
        yield new


def add_quotes2(lst):
    for i in range(len(lst)):
        line = lst[i]
        new = []
        name = "'" + line[0] + "'"
        point = "'" + line[1] + "'"
        num = line[3]
        if line[8] == 'NULL':
            mah = line[8]
            new.append(name)
            new.append(point)
            new.append(num)
            new.append(mah)
        if line[8] != 'NULL':
            mah1 = "'" + line[8] + "'"
            new.append(name)
            new.append(point)
            new.append(num)
            new.append(mah1)
        yield new


def compare_mah(base, arinc):
    for x in range(len(base)):
        line = base[x]
        route = line[0]
        point = line[2]
        for y in range(len(arinc)):
            line2 = arinc[y]
            route2 = line2[0]
            point2 = line2[1]
            if route == route2 and point == point2:
                yield line2, line[8]


def find_more40(lst):
    for i in range(len(lst)):
        line = lst[i]
        if len(line) > 40:
            new = sorted(line, key=lambda s: int(s[3]))
            yield new


def query_05_add_routes_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        query = "(%s, %s, %s, NULL, NULL, NULL, NULL, NULL, %s) \n" % (line[0], line[2], line[1], line[3])
        yield query


# Убираем наложение точек
def find_coord_trass_points(trass_points, coords):
    for i in range(len(trass_points)):
        line = trass_points[i]
        point = line[0]
        ind = line[2]
        for q in range(len(coords)):
            line2 = coords[q]
            point2 = line2[0]
            ind2 = line2[2]
            if point == point2 and ind == ind2:
                yield point, line2[1], ind


def create_order_route(lst):
    for i in range(len(lst)):
        line = lst[i]
        route = line[0][0]
        coords = []
        for q in range(len(line)):
            par = line[q]
            coord = par[4]
            coords.append(coord)
        yield route, coords


# Сопоставление трасс и точек с перерасчитанными координатами
def combine_coords(trass, coords):
    for i in range(len(trass)):
        line = trass[i]
        point = line[1]
        ind = line[2]
        for q in range(len(coords)):
            line2 = coords[q]
            point2 = line2[0]
            ind2 = line2[5]
            if point == point2 and ind == ind2:
                yield line[0], point, line[4], line[5], line[6]


def maybeMakeNumber(s):
    """Returns a string 's' into a integer if possible, a float if needed or
    returns it as is."""

    # handle None, "", 0
    if not s:
        return s
    try:
        f = float(s)
        i = int(f)
        return i if f == i else f
    except ValueError:
        return s


# Представление в нужном формате
def delta_lat(list1):
    for i in range(len(list1)):
        line = list1[i]
        output = [(line[q][1], line[q][2], line[q][3], line[q][4], line[q + 1][1], line[q + 1][2], line[q + 1][3],
                   line[q + 1][4], line[q][0]) for q in range(len(line) - 1)]
        yield output


# Измерение расстояния и угла между точками и нахождение координаты серединной точки
def distance_and_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[8]
        r = 6372795
        f1 = math.radians(int(line[1][1:3]) + int(line[1][3:5]) / 60 + int(line[1][5:7]) / 3600)
        f2 = math.radians(int(line[5][1:3]) + int(line[5][3:5]) / 60 + int(line[5][5:7]) / 3600)
        l1 = math.radians(int(line[1][10:13]) + int(line[1][13:15]) / 60 + int(line[1][15:17]) / 3600)
        l2 = math.radians(int(line[5][10:13]) + int(line[5][13:15]) / 60 + int(line[5][15:17]) / 3600)
        df = f2 - f1
        dl = l2 - l1
        a = ((math.sin(df / 2)) ** 2) + (math.cos(f1) * math.cos(f2) * (math.sin(dl / 2)) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = r * c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        f = float(fm)
        l = float(lm)
        f_gr = math.trunc(f)
        l_gr = math.trunc(l)
        f_min = math.trunc((f - f_gr) * 60)
        l_min = math.trunc((l - l_gr) * 60)
        f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
        l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
        f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
        l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
        f_gr = str(f_gr).rjust(2, '0')
        l_gr = str(l_gr).rjust(3, '0')
        f_min = str(f_min).rjust(2, '0')
        l_min = str(l_min).rjust(2, '0')
        f_sec = str(f_sec).rjust(2, '0')
        l_sec = str(l_sec).rjust(2, '0')
        f_mili = str(f_mili).rjust(2, '0')
        l_mili = str(l_mili).rjust(2, '0')
        f = 'N' + f_gr + f_min + f_sec + f_mili
        l = 'E' + l_gr + l_min + l_sec + l_mili
        coord = f + l
        yield route, fm, lm, coord, d, az, line[2], line[3]


def distance_and_angle2(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[8]
        r = 6372795
        f1 = math.radians(int(line[1][1:3]) + int(line[1][3:5]) / 60 + int(line[1][5:7]) / 3600)
        f2 = math.radians(int(line[5][1:3]) + int(line[5][3:5]) / 60 + int(line[5][5:7]) / 3600)
        l1 = math.radians(int(line[1][10:13]) + int(line[1][13:15]) / 60 + int(line[1][15:17]) / 3600)
        l2 = math.radians(int(line[5][10:13]) + int(line[5][13:15]) / 60 + int(line[5][15:17]) / 3600)
        df = f2 - f1
        dl = l2 - l1
        a = ((math.sin(df / 2)) ** 2) + (math.cos(f1) * math.cos(f2) * (math.sin(dl / 2)) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = r * c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        if d > config.d:
            f = float(fm)
            l = float(lm)
            f_gr = math.trunc(f)
            l_gr = math.trunc(l)
            f_min = math.trunc((f - f_gr) * 60)
            l_min = math.trunc((l - l_gr) * 60)
            f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
            l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
            f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
            l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
            f_gr = str(f_gr).rjust(2, '0')
            l_gr = str(l_gr).rjust(3, '0')
            f_min = str(f_min).rjust(2, '0')
            l_min = str(l_min).rjust(2, '0')
            f_sec = str(f_sec).rjust(2, '0')
            l_sec = str(l_sec).rjust(2, '0')
            f_mili = str(f_mili).rjust(2, '0')
            l_mili = str(l_mili).rjust(2, '0')
            f = 'N' + f_gr + f_min + f_sec + f_mili
            l = 'E' + l_gr + l_min + l_sec + l_mili
            coord = f + l
            yield route, fm, lm, coord, d, az, line[2], line[3]


def transform_params(lst):
    for i in range(len(lst)):
        rad = 6372795
        line = lst[i]
        lat2 = math.radians(line[1])
        lon2 = math.radians(line[2])
        lat1 = math.radians(48 + 31 / 60 + 41 / 3600)
        lon1 = math.radians(135 + 11 / 60 + 17 / 3600)
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
        x = sl1 * sl2 + cl1 * cl2 * cdelta
        ad = math.atan2(y, x)
        dist = ad * rad
        x = (cl1 * sl2) - (sl1 * cl2 * cdelta)
        y = sdelta * cl2
        z = math.degrees(math.atan(-y / x))
        if (x < 0):
            z = z + 180
        z2 = (z + 180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2 * math.pi) * math.floor((z2 / (2 * math.pi))))
        x = round(((math.sin(anglerad2) * dist) / 1000), 3)
        y = round(((math.cos(anglerad2) * dist) / 1000), 3)
        yield line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], x, y


def change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[5]
        x = line[8]
        y = line[9]
        k = (abs(x) / 300 + abs(y) / 600) * 2.5
        if a < 90 and -300 < x < 300:
            new = 90 - a
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a < 90 and -3000 < x < -300:
            new = 90 - a - k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a < 90 and 300 < x < 3000:
            new = 90 - a + k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and -300 < x < 300:
            new = 270 + (180 - a)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and -3000 < x < -300:
            new = 270 + (180 - a) - k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and 300 < x < 3000:
            new = 270 + (180 - a) + k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and -300 < x < 300:
            new = 90 - (a - 180)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and -3000 < x < -300:
            new = 90 - (a - 180) - k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and 300 < x < 3000:
            new = 90 - (a - 180) + k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and -300 < x < 300:
            new = 270 + (360 - a)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and -3000 < x < -300:
            new = 270 + (360 - a) - k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and 300 < x < 3000:
            new = 270 + (360 - a) + k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]


# Формирование слоев с эшелонами
def delete_zero_int(list):
    for i in range(len(list)):
        line = list[i]
        min = line[6]
        max = line[7]
        if min[0:2] != 'FL' and max[0:2] != 'FL' and max != 'UNLTD' and min != '     ' and min != '' and max != '':
            min = int(min)
            max = int(max)
            yield line[0], line[3], line[4], line[5], min, max
        if min[0:2] != 'FL' and max == 'UNLTD' and min != '':
            min = int(line[6])
            max = line[7]
            yield line[0], line[3], line[4], line[5], min, max
        if line[6][0:2] != 'FL' and line[7][0:2] == 'FL' and min != '':
            min = int(line[6])
            max = line[7]
            yield line[0], line[3], line[4], line[5], min, max
        if line[6][0:2] == 'FL' and line[7][0:2] == 'FL':
            yield line[0], line[3], line[4], line[5], line[6], line[7]
        if line[6][0:2] == 'FL' and line[7] == 'UNLTD':
            yield line[0], line[3], line[4], line[5], line[6], line[7]
        if min == '' and max == '':
            yield line[0], line[3], line[4], line[5], line[6], line[7]


def make_metr_mvl(list):
    for i in range(len(list)):
        line = list[i]
        min = int(round(int(line[6]) * 0.3048 * 2, -2) // 2)
        max = int(round(int(line[7]) * 0.3048 * 2, -2) // 2)
        yield line[0], line[3], line[4], line[5], min, max


def make_desw_FL(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        min = str(line[4])
        max = str(line[5])
        height = route + ':' + min + '-' + max
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
        first = 'SA: ' + sa
        third = 'T: <* BLACK * GREEN, R1> ' + coord + ' / ' + height + ' /'
        if a < 90:
            b = a * (math.pi / 180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a - 180) * (math.pi / 180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (180 - a) * (math.pi / 180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (360 - a) * (math.pi / 180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third


def make_desw2_FL(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        line2 = list2[i]
        route = line[0]
        route2 = line2[0]
        min = str(line[4])
        max = str(line[5])
        min2 = str(line2[4])
        max2 = str(line2[5])
        height = route + ':' + min + '-' + max
        height2 = route2 + ':' + min2 + '-' + max2
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
        first = 'SA: ' + sa
        third = 'T: <* BLACK * GREEN, R1> ' + coord + ' / ' + height + '; ' + height2 + '/'
        if a < 90:
            b = a * (math.pi / 180)
            dx = str(round(math.cos(b) * (1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a - 180) * (math.pi / 180)
            dx = str(round(math.cos(b) * (1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (a - 90) * (math.pi / 180)
            dx = str(round(math.cos(b) * (-1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (a - 270) * (math.pi / 180)
            dx = str(round(math.cos(b) * (-1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third


def right_format(lst1):
    for i in range(len(lst1)):
        line = lst1[i]
        coord1 = line[2]
        coord2 = line[3]
        if len(coord1) == 7 and len(coord2) == 8:
            if coord1[4:6] == '60' and coord2[5:7] == '60':
                lst = []
                lst.append(line[0])
                coord1 = coord1[0:4] + '59'
                coord2 = coord2[0:5] + '59'
                coord = 'N' + coord1 + '00' + 'E' + coord2 + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1[4:6] == '60' and coord2[5:7] != '60':
                lst = []
                lst.append(line[0])
                coord1 = coord1[0:4] + '59'
                coord = 'N' + coord1 + '00' + 'E' + coord2[0:7] + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1[4:6] != '60' and coord2[5:7] == '60':
                lst = []
                lst.append(line[0])
                coord2 = coord2[0:5] + '59'
                coord = 'N' + coord1[0:6] + '00' + 'E' + coord2 + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1 != '60' and coord2[5:7] != '60':
                lst = []
                lst.append(line[0])
                coord = 'N' + coord1[0:6] + '00' + 'E' + coord2[0:7] + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst


def midpoint_del(lst1):
    for i in range(len(lst1)):
        r = 6372795
        line = lst1[i]
        f1 = math.radians(int(line[0][1:3]) + int(line[0][3:5]) / 60 + int(line[0][5:7]) / 3600)
        l1 = math.radians(int(line[0][10:13]) + int(line[0][13:15]) / 60 + int(line[0][15:17]) / 3600)
        f2 = math.radians(int(line[1][1:3]) + int(line[1][3:5]) / 60 + int(line[1][5:7]) / 3600)
        l2 = math.radians(int(line[1][10:13]) + int(line[1][13:15]) / 60 + int(line[1][15:17]) / 3600)
        df = f2 - f1
        dl = l2 - l1
        a = ((math.sin(df / 2)) ** 2) + (math.cos(f1) * math.cos(f2) * (math.sin(dl / 2)) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = r * c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        if d > config.d:
            f = float(fm)
            l = float(lm)
            f_gr = math.trunc(f)
            l_gr = math.trunc(l)
            f_min = math.trunc((f - f_gr) * 60)
            l_min = math.trunc((l - l_gr) * 60)
            f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
            l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
            f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
            l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
            f_gr = str(f_gr).rjust(2, '0')
            l_gr = str(l_gr).rjust(3, '0')
            f_min = str(f_min).rjust(2, '0')
            l_min = str(l_min).rjust(2, '0')
            f_sec = str(f_sec).rjust(2, '0')
            l_sec = str(l_sec).rjust(2, '0')
            f_mili = str(f_mili).rjust(2, '0')
            l_mili = str(l_mili).rjust(2, '0')
            f = 'N' + f_gr + f_min + f_sec + f_mili
            l = 'E' + l_gr + l_min + l_sec + l_mili
            coord = f + l
            yield line[2], fm, lm, coord, d, az


# Перевод в прямоугольную систему координат
def transform_arinc_del(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        lat1 = math.radians(48 + 31 / 60 + 41 / 3600)
        lon1 = math.radians(135 + 11 / 60 + 17 / 3600)
        lat2 = math.radians(line[1])
        lon2 = math.radians(line[2])
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
        x = sl1 * sl2 + cl1 * cl2 * cdelta
        ad = math.atan2(y, x)
        dist = ad * rad
        x = (cl1 * sl2) - (sl1 * cl2 * cdelta)
        y = sdelta * cl2
        z = math.degrees(math.atan(-y / x))
        if (x < 0):
            z = z + 180
        z2 = (z + 180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2 * math.pi) * math.floor((z2 / (2 * math.pi))))
        # angledeg = (anglerad2*180)/math.pi
        x = round(((math.sin(anglerad2) * dist) / 1000), 3)
        y = round(((math.cos(anglerad2) * dist) / 1000), 3)
        if x > 1000 and -1000 < y < 1000:
            k = x / 250
            x = round(x + k, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x < -1000 and -1000 < y < 1000:
            k = x / 250
            x = round(x + k, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x > 1000 and y > 1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x < -1000 and y > 1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x > 1000 and y < -1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x < -1000 and y < -1000:
            k = x / 250
            x = round(x + k, 3)
            k2 = y / 250
            y = round(y + k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if -1000 < x < 1000:
            yield line[0], line[1], line[2], line[3], line[5], x, y


# Меняем угол надписи
def del_change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[4]
        x = line[5]
        y = line[6]
        k = (abs(x) / 300 + abs(y) / 600) * 2.5
        if a < 90 and -300 < x < 300:
            new = 90 - a
            yield line[0], line[3], a, new
        if a < 90 and -3000 < x < -300:
            new = 90 - a - k
            yield line[0], line[3], a, new
        if a < 90 and 300 < x < 3000:
            new = 90 - a + k
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and -300 < x < 300:
            new = 270 + (180 - a)
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and -3000 < x < -300:
            new = 270 + (180 - a) - k
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and 300 < x < 3000:
            new = 270 + (180 - a) + k
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and -300 < x < 300:
            new = 90 - (a - 180)
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and -3000 < x < -300:
            new = 90 - (a - 180) - k
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and 300 < x < 3000:
            new = 90 - (a - 180) + k
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and -300 < x < 300:
            new = 270 + (360 - a)
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and -3000 < x < -300:
            new = 270 + (360 - a) - k
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and 300 < x < 3000:
            new = 270 + (360 - a) + k
            yield line[0], line[3], a, new
