from conllu import parse

from proc.proc_file import *

from rule_g.rule_g_1 import *
from rule_g.rule_g_3 import *
from rule_g.rule_g_4 import *
from rule_g.rule_g_5 import *
from rule_g.rule_g_6 import *
from rule_g.rule_g_9 import *
from rule_g.rule_g_10 import *
from rule_g.rule_g_12 import *
from rule_g.rule_g_15_16 import *
from rule_g.rule_g_17 import *
from rule_g.rule_g_18 import *

from rule_a.rule_a_1_2_3_4_9 import *
from rule_a.rule_a_3_c1 import *
from rule_a.rule_a_3_c2 import *
from rule_a.rule_a_3_c3 import *
from rule_a.rule_a_8 import *

from rule_v.rule_v_2 import *
from rule_v.rule_v_3 import *
from rule_v.rule_v_5 import *

from rule_b.rule_b_1_2_3_4 import *

def transformation():
    name_file = input("Введите имя файла в папке tree (без формата): ")
    #name_file = "Arc_106103_1"
    #name_file = "test"
    #name_file = "Part1_10938"

    data = read_file(f"conllu/tree/{name_file}.conllu")
    if data != None:
        sentences = parse(data.read())
        for i in range(len(sentences)):
            sentence = sentences[i]
            bool_new_group = False
            print(sentence.metadata)

            bool_new_group += rule_g_15_16(sentence)

            bool_new_group += rule_a_3_c3(sentence)

            bool_new_group += rule_a_1_2_3_4_9(sentence)

            bool_new_group += rule_a_3_c2(sentence)

            bool_new_group += rule_a_8(sentence)

            bool_new_group += rule_a_3_c1(sentence)

            bool_new_group += rule_b_1_2_3_4(sentence) # Есть недочёты с b1

            bool_new_group += rule_g_12(sentence)

            bool_new_group += rule_g_17(sentence)

            #bool_new_group += rule_g_18(sentence) # Не работает / ничего не выделяет

            bool_new_group += rule_g_1(sentence)

            bool_new_group += rule_g_3(sentence)

            bool_new_group += rule_g_4(sentence)

            bool_new_group += rule_g_5(sentence)

            bool_new_group += rule_g_6(sentence)

            bool_new_group += rule_g_9(sentence) # Много брака (не уверен)

            bool_new_group += rule_g_10(sentence) # Не уверен в правильности работы

            #bool_new_group += rule_v_2(sentence) # Криво работает и много брака

            bool_new_group += rule_v_3(sentence)

            bool_new_group += rule_v_5(sentence)


    write_file(f"conllu/ssg/{name_file}.conllu", sentences)