import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import csv

newformat = 1
file = open('possesives.txt', 'r', encoding='utf-8')
poss_adj_list = file.read().split('\n')
file.close()
no_bare = 1


def split_big_file(name, size):
    big_file = open(name, 'r', encoding = 'utf-8')
    c = 0
    out = ''
    for line in big_file:
        out += line
        if c > size:
            big_file.close()
            break
        else:
            c += 1
    return out

def sort_by_position(phrase):
    i = 1
    out = []
    while len(out) != len(phrase):
        for j in phrase:
            if j.data['position'] == i:
                out.append(j)
                break
        i += 1
    return out

def get_feature(word):
    #print (word)
    pos_prons = ['мой', 'твой', 'его', 'ее', 'её', 'еe', 'eе', 'ee', 'наш', 'ваш', 'их', 'свой']
    if word.data['exact'] in pos_prons:
        return 'poss'
    cases = {'n': 'nom', 'g': 'gen', 'd': 'dat', 'a': 'acc', 'i': 'ins', 'l': 'loc', '-':'?'}

    #print(word.data['grammar'], word.data['exact'])
    if word.data['POS'] == 'N':
        for i in range(0, 1):
            try:
                return cases[word.data['grammar'][-2]]
            except:
                return cases[word.data['grammar'][-1]]
    if word.data['POS'] == 'PP':
        return word.words[0].data['exact'] + '+' + word.words[1].data['rel_feature']
    #if word.data['exact'] in possesives:
    #    return 'poss'
    if word.data['POS'] == 'V':
        for i in range(0, 1):
            try:
                return cases[word.data['grammar'][-1]]
            except:
                continue
    if is_poss(word) == 1:
        return 'poss'
    if word.data['POS'] == 'P':
        for i in range (0,1):
            try:
                return cases[word.data['grammar'][-2]]
            except:
                return morph.parse(word.data['exact'])[0].tag
    if word.data['POS'] == 'A':
        for i in range(0, 1):
            try:
                return cases[word.data['grammar'][-2]] + ' (ADJ)'
            except:
                return cases[word.data['grammar'][-1]] + ' (ADJ)'
    else:
        return str(morph.parse(word.data['exact'])[0].tag)

def is_poss(word):
    poss_list = ['мой','твой','его','ее', 'её','наш','ваш','их','свой', 'чей', 'ничей']
    if word.data['lemma'] in poss_list:
        return 1
    if 'Poss' in ' '.join([str(j.tag) for j in morph.parse(word.data['exact'])]) and 'Poss' in ' '.join([str(j.tag) for j in morph.parse(word.data['lemma'])]):
        return 1
    if  word.data['lemma'] in poss_adj_list:
        return 1
    return 0


class Conll_word:
    def __init__(self, line):
        parse = line.split()
        self.data = {}
        if newformat == 0:
            self.data['exact'] = parse[0]
            self.data['grammar'] = parse[1]
            self.data['POS'] = parse[2]
            self.data['lemma'] = parse[3]
            self.data['position'] = int(parse[4])
            self.data['parentnumber'] = int(parse[5])
            #self.data['ID'] = parse[0] + str(parse[4])
            self.data['dep_type'] = parse[6]
            self.data['children'] = []
            self.data['sentence'] = -1
            self.data['verbal'] = 1
            #print (str(is_poss(self)))



        else:
            self.data['exact'] = parse[2]
            self.data['grammar'] = parse[5]
            self.data['POS'] = parse[4]
            self.data['lemma'] = parse[3]
            self.data['position'] = int(parse[1])
            self.data['parentnumber'] = int(parse[6])
            #self.data['ID'] = parse[0] + str(parse[4])
            self.data['dep_type'] = parse[7]
            self.data['children'] = []
            self.data['sentence'] = parse[0]
            self.data['rel_feature'] = get_feature(self)



    def nominalization(self):
        #print (self.data['lemma'][-3:-1] + self.data['lemma'][-1])
        if self.data['lemma'][-3:-1] + self.data['lemma'][-1] == 'ние' or self.data['lemma'][-3:-1] + self.data['lemma'][-1]== 'тие':
            return 1
        else:
            return 0

    def __repr__(self):
        #return ' '.join([str(self.data[key]) for key in self.data])
        return self.data['exact']

    def __str__(self):
        #return ' '.join([str(self.data[key]) for key in self.data])
        return self.data['exact']

    def __iter__(self):
        for i in self.words:
            yield i

def findby(ar, featurename, featurevalue):
    for i in ar:
        if i.data[featurename] == featurevalue:
            return i
    return None

class PP(): #принимает на вход массив с conll-словами, сам является предложной группой
    def __init__(self, words):
        self.data = {}
        self.words = words
        self.data['exact'] = ' '.join([wd.data['exact'] for wd in words])
        self.data['grammar'] = words[0].data['exact'] + '+' + words[1].data['grammar']
        self.data['POS'] = 'PP'
        self.data['lemma'] = words[1].data['lemma']
        self.data['position'] = words[0].data['position']
        self.data['D_position'] = words[1].data['position']
        self.data['parentnumber'] = words[0].data['parentnumber']
        #self.data['ID'] = parse[0] + str(parse[4])
        #self.data['dep_type'] = parse[6]
        self.data['children'] = words[1].data['children']
        self.data['sentence'] = words[0].data['sentence']
        self.data['rel_feature'] = get_feature(self)
        self.data['verbal'] = 1

    def __str__(self):
        return ' '.join([wd.data['exact'] for wd in self.words])

class Sentence:
    def __init__(self, lines, *sentid):
        self.words = []
        for line in lines:
            try:
                self.words.append(Conll_word(line))
            except:
                continue
        for wd in self.words:
            if sentid:
                wd.data['sentence'] = sentid
            if wd.data['parentnumber'] != 0:
                self.words[wd.data['parentnumber']-1].data['children'].append(wd.data['position']) #присваивает узлам детей
            #print ('done')

    def traverse_depth(self, word_position, ar): #указывать word_position-1 (это переведет conll в python)
        #print (self.words[word_position].data['exact'])
        #print (self.words[word_position].data['children'])
        ar.append(self.words[word_position])
        for i in self.words[word_position].data['children']:
            #print (i)
            self.traverse_depth(i-1, ar)

    def __str__(self):
        return ' '.join([wd.data['exact'] for wd in self.words])

    def __repr__(self):
        return ' -> '.join([str(word.data['children'])+word.data['exact']+str(word.data['parentnumber']) for word in self.words])

    def nominalization(self):
        nomns = []
        for wd in self.words:
            #print (wd)
            if wd.nominalization() == 1:
                #rint (wd.data['exact'])
                nomns.append(wd)
                #return wd.data['position']
        return nomns


def rusyntax_parse(filename = 'finalcorpus.txt'):
    file  = open (filename, 'r', encoding='utf-8')
    text = file.read()
    sentences = []
    cursentence = []
    snt = 0
    for line in text.split('\n'):
        #print ('s')
        try:
            #print ('ii')
            #print (line)
            if 'SENT' not in line:
                cursentence.append(line)
            else:
                sentences.append(Sentence(cursentence, snt))
                snt += 1
                cursentence = []
        except:
            continue
    return sentences

print ('ububuibuib \n')
sentences = rusyntax_parse()
#for i in sentences:
#    print (type(i))
print (len(sentences))
def find_nominalizations(sentences): #находит все номинализации и их группы в тексте
    out = []
    for i in sentences:
        for nomn in i.nominalization():
            lst = []
            i.traverse_depth(nomn-1, lst)
            out.append(lst)
    return out
#print (sentences)


#fileout = open ('smallcorpus.txt', 'w', encoding = 'utf-8')
#fileout.write(split_big_file('../ruwac-parsed.out', 50000))
#fileout.close()
#print (sentences)
print (sentences[0])
test = []
out = ''
'''
for i in find_nominalizations(sentences):
   out += str(i[0])
   out += ' '
   out += ' '.join([str(findby(i, 'position', child)) for child in i[0].data['children']])
   #out += ''.join(str(i)) - просто запись групп целиком
   out += '\n'
'''
def nominalizations_with_children_O(sentences):
    out = []
    for i in find_nominalizations(sentences):
        locout = []
        locout.append(i[0])
        children = [findby(i, 'position', child) for child in i[0].data['children']]
        for ch in children:
            #print (type(ch))
            if morph.parse(ch.data['exact'])[0].tag.POS != None:
                if morph.parse(ch.data['exact'])[0].tag.POS == 'PREP' and ch.data['children'] != []: #если предлог - добавляет ребенка и внука номинализации
                    locout.append(PP([ch , findby(i, 'position', ch.data['children'][-1])]))
                else:
                    locout.append(ch)
        out.append((sort_by_position(locout), i[0].data['position']))
    return out


def nominalizations_with_children(sentences):
    print (type(sentences))
    allgroups = []
    cntr = 0
    for sentence in sentences:
        print (cntr)
        cntr += 1
        for nomn in sentence.nominalization():
            curgroup = []
            curgroup.append(nomn)
            for ch in nomn.data['children']:
                new = findby(sentence.words, 'position', ch)
                if new.data['exact'] not in '.,?!()-":;—"':
                    if new.data['POS'] == 'S':
                        if new.data['children'] != []:
                            new = PP([new, findby(sentence.words, 'position', new.data['children'][0])])
                    curgroup.append(new)
            allgroups.append((sort_by_position(curgroup), curgroup[0].data['position']))
    return allgroups

def nominalizations_with_children_s(sentences):
    return [nominalizations_with_children(sent) for sent in sentences]



def get_glosses(word):
    return word.data['rel_feature']
    cases = {'n': 'nom', 'g': 'gen', 'd': 'dat', 'a': 'acc', 'i': 'ins', 'l': 'loc', '-':'?'}
    possesives = ['мой','твой','его','ее','её','наш','ваш','их','свой']
    #print (is_poss(word))
    print(word.data['grammar'], word.data['exact'])
    if word.data['POS'] == 'A':
        for i in range(0, 1):
            try:
                return cases[word.data['grammar'][-2]] + ' (ADJ)'
            except:
                return cases[word.data['grammar'][-1]] + ' (ADJ)'
    if word.data['POS'] == 'N':
        for i in range(0, 1):
            try:
                return cases[word.data['grammar'][-2]]
            except:
                return cases[word.data['grammar'][-1]]
    if word.data['POS'] == 'PP':
        for i in range (0, 1):
            try:
                if word.words[1].data['POS'] != 'V':
                    return word.data['grammar'].split('+')[0] + ' + ' + cases[word.data['grammar'].split('+')[1][-2]]
                else:
                    return word.data['grammar'].split('+')[0] + ' + ' + cases[word.data['grammar'].split('+')[1][-1]]
            except:
                return word.data['grammar'].split('+')[0] + ' + ' + '?'
                continue
    if word.data['exact'] in possesives:
        return 'poss'
    if word.data['POS'] == 'P':
        for i in range (0,1):
            try:
                return cases[word.data['grammar'][-2]]
            except:
                return morph.parse(word.data['exact'])[0].tag
    else:
        return morph.parse(word.data['exact'])[0].tag

def get_model(nomwch, limit): #берет номинализацию с детьми и возвращает МУ вида [['HEAD' , 'чтение'], ['arg1', 'gen', 'книга']]
    args = []
    adjs = []
    for wd in nomwch[0]:
        if wd.data['position'] == nomwch[1]:
            args.append(['HEAD', wd.data['lemma']])
            break
    argcounter = 1
    adjcounter = 1
    for wd in nomwch[0]:
        if (wd.data['position'] > nomwch[1] or wd.data['rel_feature'] == 'poss') and len (args) < limit:
            args.append(['arg' + str(argcounter), wd.data['rel_feature'], wd.data['lemma']])
            argcounter += 1
        elif wd.data['position'] > nomwch[1]:
            adjs.append(['adj' + str(adjcounter), wd.data['rel_feature'], wd.data['lemma']])
            adjcounter += 1
    return [args, adjs]

fileout = open ('post-conll-out.csv', 'w', encoding='cp1251')
#fileout.write(out)

#fileout.write('\n'.join([' - '.join([' '.join([k.data['exact'] for k in j]) for j in i]) for i in nominalizations_with_children(sentences)]))
#fileout.write('\n'.join([' - '.join([wd.data['exact'] + '.' + str(wd.data['sentence']) for wd in line]) for line in nominalizations_with_children(sentences)]))
writer = csv.writer(fileout)
writer.writerow(['номинализация и ее зависимые', 'лемма номинализации','предложение','номинализация и ее аргументы', 'модель управления в общем виде', 'присоединяемые адъюнкты','порядок аргументов', 'вершина', '1-й аргумент', '2-ой аргумент', '1-ый адъюнкт', '2ой адъюнкт', '3ий адъюнкт', '4ый адъюнкт'])
statfile = open('statistics.csv', 'w', encoding='cp1251')
stats_w = csv.writer(statfile)

class Dict_item():
    def __init__(self, lemma):
        self.lemma = lemma
        self.amount = 1
        self.core_models = {}
        self.adjuncts = {}

    def add_model(self, model):
        if model in self.core_models:
            self.core_models[model] += 1
        else:
            self.core_models[model] = 1

    def add_adjuncts(self, adjuncts):
        if adjuncts in self.adjuncts:
            self.adjuncts[adjuncts] += 1
        else:
            self.adjuncts[adjuncts] = 1

class Stats_dict():
    def __init__(self):
        self.lemmas = {}

    def add_usage(self, lemma, model, adjuncts):
        if lemma  not in self.lemmas:
            self.lemmas[lemma] = Dict_item(lemma)
        else:
            self.lemmas[lemma].amount += 1
        self.lemmas[lemma].add_model(model)
        self.lemmas[lemma].add_adjuncts(adjuncts)

stats = Stats_dict()

def get_verbal(line):
    verbal = [wd.data['exact'] for wd in line[0] if wd.data['rel_feature'] == 'poss' or wd.data['position'] >= line[1]]
    return verbal

for line in nominalizations_with_children(sentences):
    try:
        #BARE NOMINALIZATION REMOVING
        verbal = get_verbal(line)
        if len(verbal) <= 1:
            continue

        row = []
        row.append(' - '.join([wd.data['exact']  for wd in line[0]]))
        head = [wd.data['lemma'] for wd in line[0] if wd.data['position'] == line[1]][0]
        row.append(head) # добавляет лемму
        row.append(str(sentences[line[0][0].data['sentence'][0]]))
        #row.append(' - '.join([wd.data['grammar'] for wd in line]))
        row.append(' - '.join(verbal))

        ####row.append(' - '.join([wd.data['exact'] for wd in line[0] if wd.data['rel_feature'] == 'poss' or wd.data['position'] >= line[1]]))
        #NOMINAL: row.append([get_glosses(wd) if wd.data['position'] != line[1] else 'HEAD'for wd in line[0]])
        usage = [get_glosses(wd) if wd.data['position'] != line[1] else 'HEAD' for wd in line[0] if wd.data['rel_feature'] == 'poss' or wd.data['position'] >= line[1]]
        model = [get_glosses(wd) if wd.data['position'] != line[1] else 'HEAD' for wd in line[0] if wd.data['position'] == line[1] or (get_glosses(wd) in ['poss', 'gen', 'ins'] and(wd.data['rel_feature'] == 'poss' or wd.data['position'] >= line[1]))]
        adjuncts = [get_glosses(wd) if wd.data['position'] != line[1] else 'HEAD' for wd in line[0] if get_glosses(wd) not in ['poss', 'gen', 'ins'] and(wd.data['rel_feature'] == 'poss' or wd.data['position'] >= line[1])]
        stats.add_usage(head, str(model), str(adjuncts))
        row.append(model)
        row.append(adjuncts)
        order  = []
        count = 1
        for wd in line[0]:
            if wd.data['rel_feature'] in model and wd.data['position'] != line[1]:
                order.append('arg' + str(count))
                count += 1
            elif wd.data['position'] == line[1]:
                order.append('HEAD')
            if len(order) == len(model):
                break

        '''    OLD
        for wd in line[0]: #для NOMINAL поменяй оба условия
            if wd.data['position'] > line[1] or wd.data['rel_feature'] == 'poss':
                order.append( 'arg' + str(count))
                count += 1
            elif wd.data['position'] == line[1]:
                order.append('HEAD')'''

        row.append( '-'.join(order))
        ##row.append(['arg' + str(count) if line[0][count-1].data['position'] != line[1] else 'HEAD' for count in range (1, len(line[0])+1)])
        argcount = 0
        for i in [': '.join([str(val) for val in wd]) for wd in get_model(line, len(model))[0]]:
            row.append(i)
            argcount += 1
        row.extend(['--' for cnt in range (3-argcount)]) #NEW
        for i in [': '.join([str(val) for val in wd]) for wd in get_model(line, len(model))[1]]:
            row.append(i)
        writer.writerow(row)
    except:
        continue
fileout.close()

for item in stats.lemmas:
    curitem = stats.lemmas[item]
    row = [curitem.lemma,  curitem.amount, 'модели управления', 'количество']
    stats_w.writerow(row)
    rows = []
    for model in curitem.core_models:
        rows.append(['','',model, curitem.core_models[model]])
    count = 0
    for adj_model in curitem.adjuncts:
        if len(rows) > count:
            rows[count].extend([adj_model, curitem.adjuncts[adj_model]])
        else:
            rows.append(['','','','',adj_model, curitem.adjuncts[adj_model]])
    for i in rows:
        stats_w.writerow(i)
    stats_w.writerow(['---', '---', '---', '---'])
    #stats_w.writerow(['', '', '', ''])
    #stats_w.writerow(['', '', '', ''])
statfile.close()