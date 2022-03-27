import time
import program_analyzer as PA

FILE = 'sol.log'
LOG = 'similarity.log'
EXT_LOG = 'external.log'
ignore_programs=['Migrations.sol','node_modules']
ignore_contracts=['Migrations']

class Dapp():
    def __init__(self, name, index) -> None:
        self.name = name
        self.index = index
        self.programs = []
        self.similarity = {}
        self.classes={}

    def set_programs(self, programs):
        self.programs = programs
    
    def set_classes(self):
        for p in self.programs:
            for c in p.contracts+p.interfaces+p.libraries:
                if c.sign['name'] not in self.classes.keys():
                    self.classes[c.sign['name']]=c
               
    def compare_with(self, b,mode):
        global ignore_programs
        for pa in self.programs:
            if check_ignore(ignore_programs,pa.name):
                continue
            for pb in b.programs:
                if check_ignore(ignore_programs,pb.name):
                    continue
                idx, content = program_compare(pa, pb,mode)
                if idx != 0:
                    key = b.index+' : '+b.name
                    if key not in self.similarity.keys():
                        self.similarity[key] = {}
                    self.similarity[key][pa.name+'::'+pb.name] = content

    def similarity_to_string(self):
        res = ''
        res += ((self.index+' : '+self.name).center(80, "-")+'\n')
        if len(self.similarity) == 0:
            res += ('No similar dapp\n')
            return res
        for dapp in sorted(self.similarity):
            res += ('>> '+dapp+': \n')
            res += (dic_to_string(0, self.similarity[dapp])+'\n')
        return res


def dic_to_string(idx, dic):
    res = '\t'*idx+'{'
    items = []
    for k in dic.keys():
        item = '\n'+'\t'*(idx+1) + "'" + k+"': "
        if type(dic[k]) == dict:
            item += '\n'+dic_to_string(idx+1, dic[k])
        else:
            item += str(dic[k])
        items.append(item)
    res += ','.join(items)+'\n'+'\t'*idx+'}'
    return res

def check_ignore(src,tar):
    for s in src:
        if s in tar:
            return True
    return False

def program_compare(a, b,mode):
    global ignore_contracts
    if ' '.join(a.code) == ' '.join(b.code):
        return 1, 'completely same'
    if mode=='program':
        return 0,None
    contents = {}
    flag = 0
    for ca in a.contracts:
        if ca.sign['name'] in ignore_contracts:
            continue
        for cb in b.contracts:
            if cb.sign['name'] in ignore_contracts:
                continue
            idx, content = contract_compare(ca, cb,mode)
            if idx != 0:
                contents[' '.join(ca.name)+'::'+' '.join(cb.name)] = content
                flag = 1
    return flag, contents


def contract_compare(a, b,mode):
    if ' '.join(a.name+a.code) == ' '.join(b.name+b.code):
        return 1, 'completely same'
    if mode=='contract':
        return 0,None
    if mode!='function':
        return 0,None
    contents = {}
    flag = 0
    for fa in a.functions:
        for fb in b.functions:
            idx, content = function_compare(fa, fb,mode)
            if idx != 0:
                contents[' '.join(fa.name)+'::'+' '.join(fb.name)] = content
                flag = 1
    return flag, contents


def function_compare(a, b,mode):
    if ' '.join(a.name+a.code) == ' '.join(b.name+b.code):
        return 1, 'completely same'
    if ' '.join(a.name) == ' '.join(b.name):
        return 2, 'same signature'
    # Todo: fuzzy compare
    return 0, None


def init(file):
    file_list = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith(".sol"):
                file_list.append(line)
    return file_list


def dapp_init(file_list):
    dapp_dic = {}
    for f in file_list:
        dirs = f.split('/')
        idx = dirs[1]+'/'+dirs[2]  # combine index and name
        if idx not in dapp_dic.keys():
            dapp_dic[idx] = []
        dapp_dic[idx].append(f)
    return dapp_dic


def dapp_analyzer(dapp_dic):
    dapps = []
    for key in sorted(dapp_dic):
        idx, name = key.split('/')
        dapp = Dapp(name, idx)
        program_list = dapp_dic[key]
        programs = []
        for file in program_list:
            programs.append(PA.main(file))
        dapp.set_programs(programs)
        dapp.set_classes()
        dapps.append(dapp)
    return dapps


def check_external(dapp):
    global ignore_programs,ignore_contracts
    def is_name(s):
        non = "~!@#$%^&*()+-*/<>,[]\/=;\{\}|?:"
        key = ['if', 'for','while', 'require', 'return', 'function','push',\
                'uint','int','address','string']
        for i in range(1,33):
            key.append('int'+str(i*8))
            key.append('uint'+str(i*8))
        if len(s) > 0:
            if s in key:
                return False
            for i in s:
                if i in non:
                    return False
        return True
    
    def check_instance_usage(dapp,contract): # fuzzy instance usage detection
        code=contract.code
        for word in code:
            if word in dapp.classes.keys():
                contract.sign['inherit'].append(word)

    def get_defined_tree(dapp,contract):
        funcs = list(contract.defined_names)
        inherits=contract.sign['inherit']
        if len(inherits)>0:
            funcs+=list(inherits)
            for c_name in inherits:
                if c_name in dapp.classes.keys():
                    funcs+=get_defined_tree(dapp,dapp.classes[c_name])
        return funcs

    p_dic = {}
    for p in dapp.programs:
        if check_ignore(ignore_programs,p.name):
            continue
        c_dic = {}
        for c in p.contracts:
            if c.sign['name'] in ignore_contracts:
                continue
            #check_instance_usage(dapp,c)
            funcs = get_defined_tree(dapp,c)

            f_dic = {}
            for f in c.functions:
                if len(f.sign['name'])==0:
                    continue
                external_funcs = []
                code = f.code
                code = ' '.join(code).replace(
                    '(', ' ( ').replace(
                        ')', ' ) ').replace(
                            '[', ' [ ').replace(
                                ']', ' ] ').replace(
                                    '.', ' . ').split()
                i = 0
                while i < len(code):
                    word = code[i]
                    while word != '(':
                        i += 1
                        if i >= len(code):
                            break
                        word = code[i]
                    if i >= len(code):
                        break

                    if i-1 >= 0:
                        name = code[i-1]
                        if is_name(name):
                            if name not in funcs:
                                external_funcs.append(name)
                    i += 1
                if len(external_funcs) > 0:
                    f_dic[' '.join(f.name)] = external_funcs
            if len(f_dic) > 0:
                c_dic[' '.join(c.name)] = f_dic
        if len(c_dic) > 0:
            p_dic[p.name] = c_dic
    return p_dic


def external_analyze(dapps, log):
    w = open(log, 'w')
    n = len(dapps)
    l_bar = 50
    i = 0
    print("START EXTERNAL CHECK".center(l_bar, "-"))
    start = time.perf_counter()
    for d in dapps:
        bi = int(i/(n-2)*l_bar)
        ba = "*" * bi
        bb = "." * (l_bar - bi)
        bc = (bi / l_bar) * 100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(bc, ba, bb, dur), end="")

        w.write((d.index+' : '+d.name).center(80, "-")+'\n')
        p = check_external(d)
        if len(p) == 0:
            w.write('No external function\n')
        else:
            w.write(dic_to_string(0, p)+'\n')
        i += 1
    w.close()
    print("\n"+"END EXTERNAL CHECK".center(l_bar, "-"))
    print('>> external analysis finished, results are shown in '+log)


def compare(dapps, log, mode):
    n = len(dapps)
    w = open(log, 'w')
    l_bar = 50
    print("START COMPARE".center(l_bar, "-"))
    start = time.perf_counter()
    for i in range(n):
        bi = int(i/(n-2)*l_bar)
        ba = "*" * bi
        bb = "." * (l_bar - bi)
        bc = (bi / l_bar) * 100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(bc, ba, bb, dur), end="")

        for j in range(n):
            if j==i:
                continue
            dapps[i].compare_with(dapps[j],mode)
    print("\n"+"END COMPARE".center(l_bar, "-"))

    dapp_counter = []
    for d in dapps:
        w.write(d.similarity_to_string())
        dapp_counter.append(d.index)
    # write dapps do not contain .sol file
    '''
    nonsol = []
    for i in range(1, amount+1):
        idx = '%03d' % i
        if idx not in dapp_counter:
            nonsol.append(idx)
    w.write('\nDapps without .sol file:\n'+str(nonsol)+'\n')
    '''
    w.close()
    print('>> comparing finished, results are shown in '+log)


def run_compare(mode):
    global FILE, LOG

    dapps = dapp_analyzer(dapp_init(init(FILE)))
    print('Dapps analyze finish.')

    compare(dapps, LOG, mode)


def run_external():
    global FILE, EXT_LOG

    dapps = dapp_analyzer(dapp_init(init(FILE)))
    print('Dapps analyze finish.')

    external_analyze(dapps, EXT_LOG)


def main(mode):
    global FILE, LOG, EXT_LOG

    dapps = dapp_analyzer(dapp_init(init(FILE)))
    print('Dapps analyze finish.')

    compare(dapps, LOG, mode)

    external_analyze(dapps, EXT_LOG)

    print('Done.')


# main()
