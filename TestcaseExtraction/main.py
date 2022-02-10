import os

from Extraction import Testcase_Extraction

directory = '/home/xin/Documents/scipy_data/scipy/'
path = directory + 'scipy/'

test_extrac = Testcase_Extraction()
executor_code = []
for root, dirs, files in os.walk(path):
    for file in files:
        module_name = file.replace('.py', '')
        if file.startswith('test_') \
                and file.endswith('.py') \
                and 'multiprocess' not in file \
                and 'async' not in file \
                and 'future' not in file \
                and 'concurrent' not in file:
            executor_code.extend(test_extrac.one_file(root, file, directory))

# 对每个测试用例都单独写一个本地文件
i = 0
local_call = []
path = directory + 'single_test_case'
if not os.path.exists(path):
    os.mkdir(path)

for item in executor_code:
    with open(path + '/' + str(i) + '.py', 'w') as instance_file:
        instance_file.write(item)
        instance_file.close()
    i += 1

print(i)