import datetime
import modules
import sys

# Создаем окно приложения

filename1 = input('Введите путь до старого ARINC международных трасс: ')
filename2 = input('Введите путь до нового ARINC международных трасс: ')
filename3 = input('Введите путь до дампа базы KHABAR_ANI: ')
begin_time = datetime.datetime.today()

# Выбор нужного файла
try:
    text_old = open('%s' % filename1, 'r', encoding='utf-8').readlines()
except:
    print("Неверно указан путь до старого ARINC международных трасс")
    sys.exit()

try:
    text_new = open('%s' % filename2, 'r', encoding='utf-8').readlines()
except:
    print("Неверно указан путь до нового ARINC международных трасс")
    sys.exit()

try:
    text_dump = open('%s' % filename3, 'r', encoding='utf-8').readlines()
except:
    print("Неверно указан путь до дампа базы KHABAR_ANI")
    sys.exit()

all_points_old = list(modules.get_points(text_old))
all_points_new = list(modules.get_points(text_new))

points_old = list(modules.get_data(all_points_old))
points_new = list(modules.get_data(all_points_new))

points_old = list(modules.unique(points_old))
points_new = list(modules.unique(points_new))

inside_points_old = list(modules.inside(points_old))
inside_points_new = list(modules.inside(points_new))

common_points = [x for x in inside_points_old[:] if x in inside_points_new]
non_common_points_old = [x for x in inside_points_old[:] if x not in common_points]
non_common_points_new = [x for x in inside_points_new[:] if x not in common_points]

print('x' * 100)
print('OLD_not_common_points\n')

for x in non_common_points_old:
    print(x)

print('x' * 100 + '\n')

print('NEW_not_common_points\n')
for x in non_common_points_new:
    print(x)

print('x' * 100)

names_non_common_old = list(modules.names(non_common_points_old))
names_non_common_new = list(modules.names(non_common_points_new))

common_names_diff_coord = [x for x in names_non_common_old[:] if x in names_non_common_new]

for x in common_names_diff_coord:
    print(x)
