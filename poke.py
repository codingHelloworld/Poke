#coding:utf-8
#!usr/bin/python2

import datetime
import sys
import getopt
import re
import itertools

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
    
def s(x):
    return x #12>=x>=5
def d(x):
    return x*2 #10>=x>=3
def t0(x):
    return x*3 #x*(3+0) 6>=x>=2
def t1(x):
    return x*4 #x*(3+1) 5>=x>=2
def t2(x):
    return x*5 #x*(3+2) 4>=x>=2
    
Poke_Dic = {"3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10,
            "J":11, "Q":12, "K":13, "A":14, "2":16, "X":18, "Y":19}
Poke_Dic_Inv = {"3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9", "10":"10",
            "11":"J", "12":"Q", "13":"K", "14":"A", "16":"2", "18":"joker", "19":"JOKER"}
            
#single, double, three, three1, three2, four2, four4, four, boom
Poke_Type = {"s":[1, "s", "f", "b"], "d":[2, "d", "f", "b"], "t":[3, "t", "f", "b"],
            "t1":[4, "t1", "f", "b"], "t2":[5, "t2", "f", "b"], "f2":[6, "f2", "f", "b"],
            "f4":[8, "f4", "f", "b"], "f":[4, "f", "b"], "b":[2], "sx":[0, "sx", "f", "b"],
            "dx":[0, "dx", "f", "b"], "tx":[0, "tx", "f", "b"], "tIx":[0, "tIx", "f", "b"],
                                                                "tIIx":[0, "tIIx", "f", "b"]}
Poke_Type_X = {"sx":[s, 5, 12], "dx":[d, 3, 10],
            "tx":[t0, 2, 6], "tIx":[t1, 2, 5], "tIIx":[t2, 2, 4]}
            
class Poke(object):
    EXIT = "EXIT"
    g_re_dic = {}
    g_avail_dic = {}
    g_type_value = {}
    
    @classmethod
    def usage(cls):
        print("""systrace/ftrace Help Information:
                    -h, --help:     Show help information
                    -a:             first user's poke
                    -b:             second user's poke
        """)
    
    @classmethod
    def main(cls):            
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ha:b:", ["help"])
        except getopt.GetoptError:
            cls.usage()
            sys.exit(1)
        poke_a = []
        poke_b = []
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                cls.usage()
                sys.exit()
            if opt == "-a":
                u_a = arg.upper()
                if not cls.poke_k2v(u_a, poke_a):
                    print("error input for first user")
                    sys.exit(1)
                poke_a.sort()
            if opt == "-b":
                u_b = arg.upper()
                if not cls.poke_k2v(u_b, poke_b):
                    print("error input for second user")
                    sys.exit(1)
                poke_b.sort()
        while True:
            t1 = datetime.datetime.now()
            cls.next_poke(poke_a, poke_b)
            t2 = datetime.datetime.now()
            print("Finish! (exec %ss)\n" % (t2-t1))
            poke_a = []
            poke_b = []

    @classmethod
    def next_poke(cls, poke_a, poke_b):
        while 0 == len(poke_a):
            u_a = raw_input("please input first user's poke :").upper()
            if u_a == cls.EXIT:
                print("Byebye!")
                sys.exit(2)
            if not cls.poke_k2v(u_a, poke_a):
                print("error input for first user")
                poke_a = []
                continue
            poke_a.sort()
        while 0 == len(poke_b):
            u_b = raw_input("please input second user's poke:").upper()
            if not cls.poke_k2v(u_b, poke_b):
                print("error input for second user")
                poke_b = []
                continue
            poke_b.sort()
        #print(cls.poke_next_handle([], poke_a, poke_b, "", True))
        
        poke_remain_a = poke_a
        poke_remain_b = poke_b
        poke_out_b = []
        type = ""
        while len(poke_remain_a) > 0:
            poke_out_a, poke_remain_a = cls.poke_out(
                    poke_out_b, poke_remain_a, poke_remain_b, type)
            print("\nplease select: %s" % cls.poke_v2k(poke_out_a))
            if len(poke_remain_a) == 0:
                break
            '''print("current status: f(left):%s s(left):%s s(last):%s" %
                (cls.poke_v2k(poke_remain_a), cls.poke_v2k(poke_remain_b),
                                                cls.poke_v2k(poke_out_b)))'''
            print("current status: %s %s %s" % (cls.poke_v2k(poke_remain_a),
                        cls.poke_v2k(poke_remain_b), cls.poke_v2k(poke_out_b)))
            u_b = []
            while len(u_b) == 0:
                u_b = raw_input("please input second user's select:").upper()
                poke_out_b = []
                if len(u_b) > 0:
                    if not cls.poke_k2v(u_b, poke_out_b):
                        print("error input for second user's select")
                        u_b = []
                        continue
                    poke_remain_ret, poke_remain_b = cls.poke_remain(poke_out_b, poke_remain_b)
                    if not poke_remain_ret:
                        print("error input for second user's select")
                        u_b = []
                        continue
                    #print("second user's poke: %s" % cls.poke_v2k(poke_remain_b))
                    type = cls.get_poke_type(poke_out_b)
                else:
                    type = ""
                    break
    
    @classmethod
    def get_poke_type(cls, poke_outs):
        length = len(poke_outs)
        if 1 == length:
            return "s"
        if 2 == length:
            if poke_outs[0] == poke_outs[1]:
                return "d"
            return "b"
        if 3 == length:
            return "t"
        if 4 == length:
            if poke_outs[0] == poke_outs[3]:
                return "f"
            return "t1"
        if 5 == length:
            if poke_outs[0] == poke_outs[2]:
                return "t2"
            return "5sx"
        if 6 == length:
            if poke_outs[0] == poke_outs[3]:
                return "f2"
            if poke_outs[2] - poke_outs[0] == 1 and poke_outs[5] - poke_outs[3] == 1:
                return "3dx"
            if poke_outs[2] == poke_outs[0] and poke_outs[5] == poke_outs[3]:
                return "2tx"
            return "6sx"
        if 7 == length:
            return "7sx"
        if 8 == length:
            if poke_outs[2] == poke_outs[0] and poke_outs[5] == poke_outs[3]:
                return "2tIx"
            if poke_outs[2] - poke_outs[0] == 1:
                return "4dx"
            if poke_outs[0] == poke_outs[3]:
                return "f4"
            return "8sx"
        if 9 == length:
            if poke_outs[2] == poke_outs[0]:
                return "3tx"
            return "9sx"
        if 10 == length:
            if poke_outs[2] == poke_outs[0]:
                return "2tIIx"
            if poke_outs[1] == poke_outs[0]:
                return "5dx"
            else:
                return "10sx"
        if 11 == length:
            return "11sx"
        if 12 == length:
            if(poke_outs[2] == poke_outs[0] and poke_outs[5] == poke_outs[3]
                and poke_outs[8] == poke_outs[6] and poke_outs[11] == poke_outs[9]):
                return "4tx"
            if(poke_outs[2] == poke_outs[0] and poke_outs[5] == poke_outs[3]
                                                and poke_outs[8] == poke_outs[6]):
                return "3tIx"
            if poke_outs[1] == poke_outs[0]:
                return "6dx"
            return "12sx"
        if 14 == length:
            return "7dx"
        if 15 == length:
            if poke_outs[9] == poke_outs[11]:
                return "5tx"
            return "3tIIx"
        if 16 == length:
            if poke_outs[2] == poke_outs[0]:
                return "4tIx"
            return "8dx"
        if 18 == length:
            if poke_outs[2] == poke_outs[0]:
                return "6tx"
            return "9dx"
        if 20 == length:
            if poke_outs[12] == poke_outs[14]:
                return "5tIx"
            if poke_outs[2] == poke_outs[0]:
                return "4tIIx"
            return "10dx"
        print(poke_outs)
        sys.exit(1)
    
    @classmethod
    def com_type(cls, type, type_com):
        if 0 == len(type):
            return True
        if type == type_com:
            return False
        if type_com.endswith("x"):
            return False
        return True
    
    @classmethod
    def poke_out(cls, poke_com, poke_user_a, poke_user_b, type):
        avail_poke_list = []
        if 0 == len(poke_com):
            cls.get_all_vail_poke(poke_user_a, avail_poke_list) 
        else:
            cls.get_avail_poke(poke_user_a, type, avail_poke_list)
        
        #print "avail poke list:", type, avail_poke_list
        '''print("\ncurrent status: %s %s %s" % (cls.poke_v2k(poke_user_a),
                    cls.poke_v2k(poke_user_b), cls.poke_v2k(poke_com)))'''
        #raw_input("pause")
        
        for item in avail_poke_list:
            key = item.keys()[0]
            for item_poke in item[key]:
                if cls.com_type(type, key) or item_poke[0] > poke_com[0]:
                    poke_remain_ret, poke_remain_a = cls.poke_remain(item_poke, poke_user_a)
                    if 0 == len(poke_remain_a):
                        return item_poke, poke_remain_a
        
        for item in avail_poke_list:
            key = item.keys()[0]
            for item_poke in item[key]:
                if cls.com_type(type, key) or item_poke[0] > poke_com[0]:
                    poke_remain_ret, poke_remain_a = cls.poke_remain(item_poke, poke_user_a)
                    if cls.poke_next_handle(item_poke, poke_user_b, poke_remain_a, key, False):
                        return item_poke, poke_remain_a
        if len(poke_com) > 0:
            #if cls.poke_next_handle([], poke_user_b, poke_user_a, "", False):
            return [], poke_user_a
        print("No way to win!")
        return [], []
    
    @classmethod
    def poke_k2v(cls, poke_input, poke_user):
        if 0 == len(poke_input):
            return False
        skip_0 = False
        for key in poke_input:
            if "0" == key and skip_0:
                continue
            if key == "1":
                key = "10"
                skip_0 = True
            if not Poke_Dic.has_key(key):
                return False
            poke_user.append(Poke_Dic[key])
        return True
        
    @classmethod
    def poke_v2k(cls, poke_v):        
        if 0 == len(poke_v):
            return "Pass"
        poke_out_str = ""
        for key in poke_v:
            poke_out_str += Poke_Dic_Inv[str(key)]
        return poke_out_str
            
    
    @classmethod
    def poke_type_value(cls, poke_user, type, length):
        type_key = str(poke_user)+type+str(length)
        if cls.g_type_value.has_key(type_key):
            return cls.g_type_value[type_key]
        
        size = len(poke_user)
        if size < length:
            return []
        ret = []
        if "s" == type:
            poke_set = set(poke_user)
            for item in poke_set:
                ret.append([item])
        elif "d" == type:
            i = 0
            while i < (size - 1):
                if poke_user[i+1] == poke_user[i]:
                    ret.append([poke_user[i], poke_user[i]])
                    while (i < size - 1) and poke_user[i+1] == poke_user[i]:
                        i = i + 1
                i = i + 1
        elif "t" == type:
            i = 0
            while i < (size - 2):
                if poke_user[i+2] == poke_user[i]:
                    if i+3 < size and poke_user[i+3] == poke_user[i]:
                        i = i + 3
                    else:
                        i = i + 2
                    ret.append([poke_user[i], poke_user[i], poke_user[i]])
                i = i + 1
        elif "t1" == type:
            t_list = cls.poke_type_value(poke_user, "t", Poke_Type["t"][0])
            for item in t_list:
                for s_item in set(poke_user):
                    if s_item != item[0]:
                        ret.append([item[0], item[0], item[0], s_item])
        elif "t2" == type:
            d_list = cls.poke_type_value(poke_user, "d", Poke_Type["d"][0])
            t_list = cls.poke_type_value(poke_user, "t", Poke_Type["t"][0])
            for item in t_list:
                for d_item in d_list:
                    if d_item[0] != item[0]:
                        ret.append([item[0], item[0], item[0], d_item[0], d_item[0]])
        elif "f" == type:
            i = 0
            while i < (size - 3):
                if poke_user[i+3] == poke_user[i]:
                    i = i + 3
                    ret.append([poke_user[i], poke_user[i], poke_user[i], poke_user[i]])
                i = i + 1
        elif "f2" == type:
            f_list = cls.poke_type_value(poke_user, "f", Poke_Type["f"][0])
            for f_item in f_list:
                s_list = list(poke_user)
                while f_item[0] in s_list:
                    s_list.remove(f_item[0])
                com_f_set = set(list(itertools.combinations(s_list, 2)))
                for item in com_f_set:
                    ret.append([f_item[0], f_item[0], f_item[0], f_item[0], item[0], item[1]])
        elif "f4" == type:
            d_list = cls.poke_type_value(poke_user, "d", Poke_Type["d"][0])
            if len(d_list) < 3:
                return []
            f_list = cls.poke_type_value(poke_user, "f", Poke_Type["f"][0])
            for f_item in f_list:
                d2s_list = []
                for d_item in d_list:
                    if d_item[0] != f_item[0]:
                        d2s_list.append(d_item[0])
                com_f_list = list(itertools.combinations(d2s_list, 2))
                for item in com_f_list:
                    ret.append([f_item[0], f_item[0], f_item[0], f_item[0],
                                                            item[0], item[0], item[1], item[1]])
        elif "b" == type:
            if Poke_Dic["X"] in poke_user and Poke_Dic["Y"] in poke_user:
                ret.append([Poke_Dic["X"], Poke_Dic["Y"]])
        elif type.endswith("x"):
            index = int(re.findall("\\d+", type)[0])
            if type.endswith("sx"):
                poke_user_list = list(set(poke_user))
                poke_user_list.sort()
                size = len(poke_user_list)
                if size < length:
                    return []
                i = 0
                while i + index <= size:
                    is_s = True
                    s_list = [poke_user_list[i]]
                    j = 1
                    while j < index:
                        if j != (poke_user_list[i+j] - poke_user_list[i]):
                            i = i + j
                            is_s = False
                            break
                        s_list.append(poke_user_list[i+j])
                        j = j + 1
                    if is_s:
                        ret.append(s_list)
                        i = i + 1
            elif type.endswith("dx"):
                d_list = cls.poke_type_value(poke_user, "d", Poke_Type["d"][0])
                if len(d_list) < 3:
                    return []
                poke_user_list = []
                for item in d_list:
                    poke_user_list.append(item[0])
                poke_user_list.sort()
                size = len(poke_user_list)
                if size*2 < length:
                    return ret
                sx_list = cls.poke_type_value(poke_user_list, str(index)+"sx", index)
                for sx_item in sx_list:
                    dx_list = []
                    for s_item in sx_item:
                        dx_list.extend([s_item, s_item])
                    ret.append(dx_list)
            elif type.endswith("tx"):
                t_list = cls.poke_type_value(poke_user, "t", Poke_Type["t"][0])
                if len(t_list) < 2:
                    return []
                poke_user_list = []
                for item in t_list:
                    poke_user_list.append(item[0])
                poke_user_list.sort()
                size = len(poke_user_list)
                if size*3 < length:
                    return ret
                sx_list = cls.poke_type_value(poke_user_list, str(index)+"sx", index)
                for sx_item in sx_list:
                    dx_list = []
                    for s_item in sx_item:
                        dx_list.extend([s_item, s_item, s_item])
                    ret.append(dx_list)
            elif type.endswith("tIx"):
                tx_list = cls.poke_type_value(poke_user, str(index)+"tx", index*3)
                for tx_item in tx_list:
                    poke_tIx_list = list(poke_user)
                    for i in range(index):
                        for j in range(3):
                            poke_tIx_list.remove(tx_item[i*3])
                    tIx_suf_set = set(list(itertools.combinations(poke_tIx_list, index)))
                    for item in tIx_suf_set:
                        s_list_copy = list(tx_item)
                        s_list_copy.extend(item)
                        ret.append(s_list_copy)
            elif type.endswith("tIIx"):
                d_list = cls.poke_type_value(poke_user, "d", Poke_Type["d"][0])
                s_list = []
                for d_item in d_list:
                    s_list.append(d_item[0])
                    if 4 == poke_user.count(d_item[0]):
                        s_list.append(d_item[0])
                if len(s_list) < 2*index:
                    return []
                tx_list = cls.poke_type_value(poke_user, str(index)+"tx", index*3)
                for tx_item in tx_list:
                    poke_tIx_list = list(s_list)
                    for i in range(index):
                        while tx_item[i*3] in poke_tIx_list:
                            poke_tIx_list.remove(tx_item[i*3])
                    tIx_suf_set = set(list(itertools.combinations(poke_tIx_list, index)))
                    for item in tIx_suf_set:
                        s_list_copy = list(tx_item)
                        for i in range(index):
                            s_list_copy.extend([item[i], item[i]])
                        ret.append(s_list_copy)
            else:
                print "error param:", type
                sys.exit(1)
        else:
            print "error param:", type
            sys.exit(1)
        cls.g_type_value[type_key] = list(ret)
        return ret
        
    @classmethod
    def poke_next_handle(cls, poke_com, poke_user_a, poke_user_b, type, want_win):
        re_dic_key = str(poke_com)+str(poke_user_a)+str(poke_user_b)+str(type)+str(want_win)
        if cls.g_re_dic.has_key(re_dic_key):
            return cls.g_re_dic[re_dic_key]
        
        avail_poke_list = []
        if 0 == len(poke_com):
            cls.get_all_vail_poke(poke_user_a, avail_poke_list) 
        else:
            cls.get_avail_poke(poke_user_a, type, avail_poke_list)
        
        '''
        print type, avail_poke_list
        print poke_user_a, poke_user_b, want_win
        '''
        
        for item in avail_poke_list:
            key = item.keys()[0]
            for item_poke in item[key]:
                if cls.com_type(type, key) or item_poke[0] > poke_com[0]:
                    poke_remain_ret, poke_remain_a = cls.poke_remain(item_poke, poke_user_a)
                    if 0 == len(poke_remain_a):
                        if want_win:
                            cls.g_re_dic[re_dic_key] = True
                            return True
                        else:
                            cls.g_re_dic[re_dic_key] = False
                            return False
        
        if want_win:
            ret = False
        else:
            ret = True
        for item in avail_poke_list:
            key = item.keys()[0]
            for item_poke in item[key]:
                if cls.com_type(type, key) or item_poke[0] > poke_com[0]:
                    poke_remain_ret, poke_remain_a = cls.poke_remain(item_poke, poke_user_a)
                    handle_ret = cls.poke_next_handle(
                                    item_poke, poke_user_b, poke_remain_a, key, not want_win)
                    if want_win:
                        if handle_ret:
                            cls.g_re_dic[re_dic_key] = True
                            return True
                    else:
                        if not handle_ret:
                            cls.g_re_dic[re_dic_key] = False
                            return False
        if len(poke_com) > 0:
            handle_ret = cls.poke_next_handle([], poke_user_b, poke_user_a, "", not want_win)
            if want_win:
                if handle_ret:
                    cls.g_re_dic[re_dic_key] = True
                    return True
            else:
                if not handle_ret:
                    cls.g_re_dic[re_dic_key] = False
                    return False
        cls.g_re_dic[re_dic_key] = ret
        return ret
        
        
    @classmethod
    def get_all_vail_poke(cls, poke_user, avail_poke_list):
        types = Poke_Type.keys()
        for type in types:
            cls.get_avail_poke(poke_user, type, avail_poke_list)
        
    @classmethod
    def get_avail_poke(cls, poke_user, type, avail_poke_list):
        key_dic = str(poke_user)+type
        if cls.g_avail_dic.has_key(key_dic):
            for item_cache in cls.g_avail_dic[key_dic]:
                if item_cache not in avail_poke_list:
                    avail_poke_list.append(item_cache)
            return
        new_type = type
        index_fix = -1
        if not Poke_Type.has_key(type):
            new_type = re.findall("[A-Za-z]+", type)[0]
            index_fix = int(re.findall("\\d+", type)[0])
        avail_type_list = list(Poke_Type[new_type])
        length = avail_type_list.pop(0)
        type_list = []
        for item_type in avail_type_list:
            if item_type in Poke_Type_X.keys():
                type_x_list = list(Poke_Type_X[item_type])
                if index_fix > 0:
                    value_list = cls.poke_type_value(poke_user, type, type_x_list[0](index_fix))
                    if len(value_list) > 0 and {type:value_list} not in avail_poke_list:
                        type_list.append({type:value_list})
                else:
                    for index in range(type_x_list[1], type_x_list[2] + 1):
                        value_list = cls.poke_type_value(poke_user, str(index)+item_type,
                                                                    type_x_list[0](index))
                        if len(value_list) == 0:
                            break
                        if {str(index)+item_type:value_list} not in type_list:
                            type_list.append({str(index)+item_type:value_list})
            else:
                value_list = cls.poke_type_value(poke_user, item_type, length)
                if len(value_list) > 0 and {item_type:value_list} not in type_list:
                    type_list.append({item_type:value_list})
        if len(type_list) > 0:
            cls.g_avail_dic[key_dic] = list(type_list)
            for item in type_list:
                if item not in avail_poke_list:
                    avail_poke_list.append(item)
                
    @classmethod
    def poke_remain(cls, poke_outs, poke_user):
        poke_list = list(poke_user)
        for item in poke_outs:
            if item in poke_list:
                poke_list.remove(item)
            else:
                return False, poke_user
        return True, poke_list
            

if __name__ == "__main__":
    Poke.main()