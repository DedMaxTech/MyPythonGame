import glob

dir = 'D:/Projects/Python/MyPythonGame/'

files = glob.glob(dir+'*.py') + glob.glob(dir+'game/*.py') + glob.glob(dir+'game/fx/*.py')
lines = {}
for f in files:
    with open(f,'r') as file:
        lines[f]=len(file.readlines())
lines= {k: v for k, v in sorted(lines.items(), key=lambda item: item[1],reverse=True)}
print(' '*29,sum(lines.values()))
for k, v in lines.items(): print(k.split('\\')[-1].ljust(30)+str(v))