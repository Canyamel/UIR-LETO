from rule_b.rule_b_1 import *
from rule_b.rule_b_2 import *
from rule_b.rule_b_3 import *
from rule_b.rule_b_4 import *


#Последовательное выделение всех подкритериев Б
def rule_b_1_2_3_4(sentence: TokenList) -> bool:
    bool_new_group = False
    bool_new_group = rule_b_2(sentence)
    bool_new_group += rule_b_1_BSP(sentence)
    bool_new_group += rule_b_1_vd_souz(sentence)
    bool_new_group += rule_b_1_odnorod(sentence)
    bool_new_group += rule_b_1_predl(sentence)
    for token_b2_b1 in sentence.filter(xpos='Б2') + sentence.filter(xpos='Б1'):
        current_token = get_head(token_b2_b1, sentence)
        while True:
            if current_token['head'] == 1 or current_token['id'] == 1 or token_b2_b1['upos'] in current_token['upos']:
                break
            elif current_token['xpos'] in ('Б2', 'Б1'):
                token_b2_b1['head'] = current_token['id']
                break
            current_token = get_head(current_token, sentence)

    bool_new_group += rule_b_4(sentence)
    bool_new_group += rule_b_3(sentence)

    return bool_new_group