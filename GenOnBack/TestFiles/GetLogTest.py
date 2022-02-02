import os

tmp_file_name = 'TestFile.py'
result = []
try:
    result = os.popen('python3.8 ' + tmp_file_name).read().splitlines()
except:
    pass

print_addre = False
print_cond = False
address = []
address_map = {}
for line in result:
    if 'pycing address start' in line:
        print_addre = True
        continue
    elif 'pycing address end' in line:
        print_addre = False
    if print_addre and line.startswith('address:'):
        address.append(line[10:])
        address_map[line[10:]] = []

    if 'pycing native start' in line:
        print_cond = True
        continue
    elif 'pycing native end' in line:
        break
    if print_cond:
        for one_add in address:
            if one_add in line:
                address_map[one_add].append(line[7:line.index("&")])

print(address_map)