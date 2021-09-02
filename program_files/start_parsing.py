import os
from sys import argv

try:
    if argv[1] == "-h" or argv[1] == "?" or argv[1] == "--help":
        os.system('python3 ./app/help.py')
    elif argv[1] == "-c" or argv[1] == "--check":
        os.system('python3 ./app/checking.py')
    elif argv[1] == "-s" or argv[1] == "--sintez":
        os.system('python3 ./app/sintez_parsing.py')
    elif argv[1] == "-k" or argv[1] == "--korinf":
        os.system('python3 ./app/korinf_parsing.py')
    elif argv[1] == "o" or argv[1] == "--orla":
        os.system('python3 ./app/radar_screen_orl_parsing.py')
    else:
        print(f'Вы ввели неправильный ключ, для справочной информации\n'
              f'введите -h, --help или ?')
except:
    print(f'Вы не ввели ключ. Для отображения всех ключей\n'
          f'введите рядом и именем скрипта -h или --help или ?')
