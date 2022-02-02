import subprocess

p = subprocess.Popen('dir', shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
while(True):
    buff = p.stdout.readline()
    if buff == '' and p.poll() != None:
        break
    print(buff)