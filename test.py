from importlib.machinery import SourceFileLoader

path = '/home/polina/Docker_image/app/my_script.py'
module_name = 'my_script'

loader = SourceFileLoader(module_name, path)
module = loader.load_module()

test1 = module.a
print(test1)