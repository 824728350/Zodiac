import subprocess
from threading import Timer
from collections import defaultdict
import ipaddress
import z3 

def execute_cmd_all(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = ""
    while True:
        if process.poll() is not None:
            break
        output = process.stdout.readline()
        if output:
            result += output.strip().decode() + "\n"
    #timer.start()
    process.wait()
    if (process.returncode):
        #print("get a problem")
        return result
    return result

def execute_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    timer = Timer(60, process.kill)
    timer.start()
    result = ""
    while True:
        if process.poll() is not None:
            break
        output = process.stdout.readline()
        if output:
            result += output.strip().decode() + "\n"
    #timer.start()
    process.wait()
    if (process.returncode):
        #print("get a problem")
        return "Failure"
    return result

def execute_cmd_imm(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = ""
    while True:
        if process.poll() is not None:
            break
        output = process.stdout.readline()
        if output:
            result += output.strip().decode() + "\n"
    #timer.start()
    process.wait()
    if (process.returncode):
        #print("get a problem")
        return "Failure"
    return result

def execute_cmd_err(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = ""
    while True:
        if process.poll() is not None:
            break
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output:
            result += output.strip().decode() + "\n"
        if error:
            result += error.strip().decode() + "\n"
    #timer.start()
    process.wait()
    if (process.returncode):
        #print("get a problem")
        return result
    return result

def execute_cmd_details(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = ""
    while True:
        if process.poll() is not None:
            break
        output = process.stdout.readline()
        if output:
            result += output.strip().decode() + "\n"
    #timer.start()
    process.wait()
    return result

def find_nth(haystack, needle, n):
    if n > 0:
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+len(needle))
            n -= 1
        return start
    elif n < 0:
        haystack = haystack[::-1]
        n *= -1
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+len(needle))
            n -= 1
        return len(haystack) - start - 1

class DSU:
    def __init__(self):
        self.parent = defaultdict(str)
        self.rank = defaultdict(int)
    def find(self,x):
        if x != self.parent[x]:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self,x,y):
        xr, yr = self.find(x), self.find(y)
        if xr == yr:
            return False
        elif self.rank[xr] > self.rank[yr]:
            self.parent[yr] = xr
        elif self.rank[xr] < self.rank[yr]:
            self.parent[xr] = yr
        else:
            self.parent[yr] = xr
            self.rank[xr] += 1
        return True

def ip_to_bv(ip):
    parts = [int(x) for x in ip.split(".")]
    return z3.Concat([z3.BitVecVal(x, 8) for x in parts])

def len_to_mask(len):
    return str(ipaddress.IPv4Network(f'0.0.0.0/{len}').netmask)

def bv_to_ip(bv):
    # Check if the bitvector is of size 32
    if bv.size() == 32:
        parts = [z3.Extract(i * 8 + 7, i * 8, bv) for i in range(4)]
        #print(parts)
        parts = [z3.simplify(z3.ZeroExt(24, x)).as_long() for x in parts]
        #print(parts)
        ip = ".".join([str(x) for x in parts][::-1])
        return ip
    else:
        return None