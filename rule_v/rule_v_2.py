from proc.proc_conllu import *

def _rule_v_2(sentence: TokenList) -> bool:
    bool_new_group = False
    memory = []

    for token in sentence:
        if token['deprel'] == "сравн-союзн" or token['deprel'] == "соч-союзн" or token['deprel'] == "инф-союзн"or token['deprel'] == "подч-союзн": # поиск любых словосочетаний, вводимых союзами
            k = 1
            ht = get_head(token, sentence)
            memory.append((ht['form'], token['form'], token['deprel']))
            child_tokens = get_one_step_children_token(token, sentence)
            token_phrase = ht['form']
            normal_children = []

            if(ht['form'] == None):
                return 0

            # проверка, чтобы в словосочетании не было частиц, союзов и предлогов, чего по факту быть не должно
            # и от чего надо, бы избавиться, но на данном этапе и так сойдет
            for child in child_tokens:
                if child['xpos'] != 'PR' and child['form'] != None and child['upos'] != 'CCONJ' and child['upos'] != 'PART':
                    normal_children.append(child)
                    k += 1
                else:
                    grands = get_one_step_children_token(child, sentence)
                    for g in grands:
                        if g['xpos'] != 'PR' and g['form'] != None and g['form'] != '_' and g['upos'] != 'CCONJ' and g['upos'] != 'PART':
                                k += 1
                                normal_children.append(g)
            normal_children.append(token)

            if k > 1:
                bool_new_group = True
                token_phrase = ""
                normal_children.sort(key=lambda token: token['id'])
                for t in sentence:
                    token_phrase += t['form'] + ' '
                token_phrase = token_phrase[:-1]

                sentence.append(create_sg(len(sentence) + 1, token_phrase, 'В2', ht['head'], ht['deprel']))
                ht['deprel'] = '_'
                ht['head'] = len(sentence)
                #token['deprel'] = '_'

                #for reb_token in normal_children:
                #    cur_children_token = get_one_step_children_token(reb_token, sentence)
                #    for t in cur_children_token:
                #        if t not in normal_children:
                #            t['head'] = len(sentence)
    '''
    for token in sentence:
        h = get_head(token, sentence)
        for m in memory:
            if m[0] == h['form'] and m[1] == token['form'] and token['deprel'] == '_':
                token['deprel'] = m[2]
    '''
    return bool_new_group

def get_id(element):
    return element['id']
def rule_v_2(sentence: TokenList) -> bool:
    bool_new_group = False
    memory = []
    for t in sentence:
        if t['deprel'] == "сравн-союзн" or t['deprel'] == "соч-союзн" or t['deprel'] == "инф-союзн"or t['deprel'] == "подч-союзн": # поиск любых словосочетаний, вводимых союзами
            k = 1
            ht = get_head(t, sentence)
            memory.append((ht['form'], t['form'], t['deprel']))
            child_tokens = get_one_step_children_token(t, sentence)

            normal_children = []
            if(ht['form'] == None):
                return 0

            # проверка, чтобы в словосочетании не было частиц, союзов и предлогов, чего по факту быть не должно
            # и от чего надо, бы избавиться, но на данном этапе и так сойдет
            for child in child_tokens:
                if child['xpos'] != 'PR' and child['form'] != None and child['upos'] != 'CCONJ' and child['upos'] != 'PART':
                    normal_children.append(child)
                    k=k+1
                else:
                    grands = get_one_step_children_token(child, sentence)
                    for g in grands:
                        if g['xpos'] != 'PR' and g['form'] != None and g['form'] != '_' and g['upos'] != 'CCONJ' and g['upos'] != 'PART':
                                k = k+1
                                normal_children.append(g)
            normal_children.append(t)

            if k > 1:
                bool_new_group = True
                normal_children.append(ht)
                token_phrase = ''
                normal_children.sort(key=lambda token: token['id'])
                for t in normal_children:
                    token_phrase += t['form'] + ' '
                token_phrase = token_phrase[:-1]

                new_token = create_sg(len(sentence) + 1, token_phrase, 'В2', ht['head'], ht['deprel'])
                sentence.append(new_token)
                ht['deprel'] = "_"
                ht['head'] = len(sentence)

                #for reb_token in normal_children:
                #    cur_children_token = get_one_step_children_token(reb_token, sentence)
                #    for t in cur_children_token:
                #        if t not in normal_children:
                #            t['head'] = len(sentence)
    '''
    for t in sentence:
        h = get_head(t, sentence)
        for m in memory:
            if m[0] == h['form'] and m[1] == t['form'] and t['deprel'] == '_':
                t['deprel'] = m[2]
    '''
    return bool_new_group