from proc.proc_conllu import *

def rule_b_1_predl(sentence: TokenList) -> bool: #Выделение двух предложно-падежных групп существительных, упомянутых в В5
    bool_new_group = False

    key_tokens_list = []
    head_token_list = []
    head_token_childs_list = []
    text_group = ""
    for token in sentence:
        if token['form'] is None:
            continue

        if token['deprel'] == 'соотнос':
            key_tokens_list.append(token)

    for key_token in key_tokens_list:
        head_token = get_head(key_token,sentence)
        children_token = get_one_step_children_token(key_token, sentence)
        if len(children_token) == 1:
            true_child = children_token[0]
        else:
            continue

        if true_child['upos'] == 'NOUN' and true_child['deprel'] == 'предл' and head_token['upos']=='ADP':
            for current_token in get_one_step_children_token(head_token, sentence):
                if current_token['upos']=='NOUN' and current_token['deprel']=='предл':
                    head_token_list.append(head_token)

    for head_token_el in head_token_list:
        head_token_childs_list = get_children_token(head_token_el, sentence)
        head_token_childs_list.append(head_token_el)

        buf_head_token_childs_list = head_token_childs_list.copy()
        for t in head_token_childs_list:
            if t['lemma'] == '_':
                buf_head_token_childs_list.remove(t)
                components_sg = get_group_all_component_sg(t, sentence)
                for cmp in components_sg:
                    if cmp not in buf_head_token_childs_list:
                        buf_head_token_childs_list.append(cmp)

        buf_head_token_childs_list.sort(key=lambda token: token['id'])
        for t in buf_head_token_childs_list:
            text_group += t['form'] + ' '
        text_group = text_group[:-1]

        new_token = create_sg(len(sentence) + 1, text_group, 'Б1', head_token_el['head'], head_token_el['deprel'])
        sentence.append(new_token)

        text_group = ''
        bool_new_group = True
        head_token_el['deprel'] = '_'
        head_token_el['head'] = len(sentence)

        for reb_token in head_token_childs_list:
            cur_children_token = get_one_step_children_token(reb_token, sentence)
            for t in cur_children_token:
                if t not in head_token_childs_list:
                    t['head'] = len(sentence)

        head_token_childs_list = []

    return bool_new_group


#рекурсивная функция получения токенов, которые будут составлять подчинительную часть, выделяемую союзами по Б1
def get_child_recursive_with_rebinding_part_b1_vd_souz(head_token, sentence, child_tokens_array, exception_array):
    for tok in sentence:
        if tok['form'] is None and tok['xpos'] not in ['Б2', 'Б3', 'Б4'] and head_token != tok:
            continue

        elif tok['xpos'] in ['Б3', 'Б4'] and head_token != tok:
            child_tokens_array = get_child_recursive_with_rebinding_part_b1_BSP(tok, sentence, child_tokens_array, exception_array)

        if tok['head'] == head_token['id']:
            if tok not in exception_array and tok['xpos'] != 'Б2':
                if tok['upos'] == 'CCONJ':
                    if tok['deprel'] == 'сочин' and len(get_one_step_children_token(tok, sentence)) == 1 and get_head(tok,sentence)['upos'] == get_one_step_children_token(tok, sentence)[0]['upos'] and get_head(tok, sentence)['upos']!='VERB':
                        child_tokens_array.append(tok)
                        child_tokens_array = get_child_recursive_with_rebinding_part_b1_vd_souz(tok, sentence, child_tokens_array, exception_array)
                    else:
                        continue
                else:
                    child_tokens_array.append(tok)
                    child_tokens_array = get_child_recursive_with_rebinding_part_b1_vd_souz(tok, sentence, child_tokens_array, exception_array)
    return child_tokens_array

#выделение части СП, вводимые союзами
def rule_b_1_vd_souz(sentence: TokenList) -> bool:
    bool_new_group = False
    head_tokens_list = []
    text_group = ''
    good_podch_deprels = ['эксплет', 'сент-соч', 'изъясн', 'сравнит', 'предик', 'вводн', 'обст', '1-компл', '2-компл',
                            '3-компл', '4-компл', '1-несобст-компл', '1-несобст-компл', '2-несобст-компл', '3-несобст-компл', '4-несобст-компл', 'атриб',
                            'об-копр', 'суб-копр']
    head_token_childs_list = []

    #Выделение головёшек СГ
    for token in sentence:
        if token['form'] is None:
            continue

        if token['deprel'] in ('подч-союзн', 'сравн-союзн') and get_head(token, sentence)['upos'] == 'CCONJ' and get_head(token, sentence)['id'] not in get_all_id(head_tokens_list):
            head_tokens_list.append(get_head(token, sentence))

        elif token['deprel'] in good_podch_deprels and token['upos'] == 'CCONJ' and token['id'] not in get_all_id(head_tokens_list):
            head_tokens_list.append(token)

    for head_token in head_tokens_list:
        head_token_childs_list = get_child_recursive_with_rebinding_part_b1_vd_souz(head_token, sentence, head_token_childs_list, head_tokens_list)
        head_token_childs_list.append(head_token)

        buf_head_token_childs_list = head_token_childs_list.copy()
        for t in head_token_childs_list:
            if t['lemma'] == '_':
                buf_head_token_childs_list.remove(t)
                components_sg = get_group_all_component_sg(t, sentence)
                for cmp in components_sg:
                    if cmp not in buf_head_token_childs_list:
                        buf_head_token_childs_list.append(cmp)

        buf_head_token_childs_list.sort(key=lambda token: token['id'])
        for t in buf_head_token_childs_list:
            text_group += t['form'] + ' '
        text_group = text_group[:-1]

        new_token = create_sg(len(sentence) + 1, text_group, 'Б1', head_token['head'], head_token['deprel'])
        sentence.append(new_token)

        text_group = ''
        bool_new_group = True
        head_token['deprel'] = '_'
        head_token['head'] = len(sentence)

        for reb_token in head_token_childs_list:
            cur_children_token = get_one_step_children_token(reb_token, sentence)
            for t in cur_children_token:
                if t not in head_token_childs_list:
                    t['head'] = len(sentence)

        head_token_childs_list = []

    return bool_new_group


#рекурсия для выделения токенов, составляющих СГ из однородных членов предложения.
def get_child_recursive_with_rebinding_part_b1_odnorod(head_token, sentence, child_tokens_array, exception_array):
    for tok in sentence:
        if tok['form'] is None and tok['xpos'] not in ['Б2', 'Б3', 'Б4'] and head_token != tok:
            continue

        elif tok['xpos'] in ['Б3', 'Б4'] and head_token != tok:
            child_tokens_array = get_child_recursive_with_rebinding_part_b1_BSP(tok, sentence, child_tokens_array, exception_array)

        if tok['head'] == head_token['id']:
            if tok not in exception_array and tok['xpos'] != 'Б2':
                child_tokens_array.append(tok)
                child_tokens_array = get_child_recursive_with_rebinding_part_b1_odnorod(tok, sentence, child_tokens_array, exception_array)

    return child_tokens_array


#Выделение СГ с однородными членами предложения
def rule_b_1_odnorod(sentence: TokenList) -> bool:
    bool_new_group = False
    text_group = ''
    head_tokens_list = []
    head_token_childs_list = []

    for token in sentence:
        if token['form'] is None:
            continue

        if (token['deprel'] == 'сочин' and token['upos'] == get_head(token, sentence)['upos']) or \
                (token['deprel'] == 'соч-союзн' and get_head(token, sentence)['deprel'] == 'сочин' and
                get_head(get_head(token, sentence), sentence)['upos'] == token['upos']) and token['upos'] != 'VERB':
            head_token = get_head(token, sentence)

            while head_token['deprel'] in ('сочин', 'соч-союзн') or (head_token['upos'] == 'CCONJ' and head_token['deprel'] == 'сочин'):
                if head_token['head'] == 1:
                    break
                head_token = get_head(head_token, sentence)

            if head_token['deprel'] == 'предл':
                head_token = get_head(head_token, sentence)

            if head_token not in head_tokens_list:
                head_tokens_list.append(head_token)

    for head_token in head_tokens_list:
        head_token_childs_list = get_child_recursive_with_rebinding_part_b1_odnorod(head_token, sentence, head_token_childs_list, head_tokens_list)
        head_token_childs_list.append(head_token)

        buf_head_token_childs_list = head_token_childs_list.copy()
        for t in head_token_childs_list:
            if t['lemma'] == '_':
                buf_head_token_childs_list.remove(t)
                components_sg = get_group_all_component_sg(t, sentence)
                for cmp in components_sg:
                    if cmp not in buf_head_token_childs_list:
                        buf_head_token_childs_list.append(cmp)

        buf_head_token_childs_list.sort(key=lambda token: token['id'])
        for t in buf_head_token_childs_list:
            text_group += t['form'] + ' '
        text_group = text_group[:-1]

        new_token = create_sg(len(sentence) + 1, text_group, 'Б1', head_token['head'], head_token['deprel'])
        sentence.append(new_token)

        text_group = ''
        bool_new_group = True
        head_token['deprel'] = '_'
        head_token['head'] = len(sentence)

        #print(head_token_childs_list)
        for reb_token in head_token_childs_list:
            if reb_token['deprel'] == 'сочин' or reb_token['deprel'] == 'соч-союзн':
                reb_token['deprel'] = '_'
                reb_token['head'] = len(sentence)
            cur_children_token = get_one_step_children_token(reb_token, sentence)
            for t in cur_children_token:
                if t not in head_token_childs_list:
                    t['head'] = len(sentence)

        head_token_childs_list = []

    return bool_new_group


#Выделение токенов, составляющих часть бессоюзного сложного предложения
def get_child_recursive_with_rebinding_part_b1_BSP(head_token, sentence, child_tokens_array, exception_array):
    for tok in sentence:
        if tok['form'] is None and tok['xpos'] not in ['Б2', 'Б3', 'Б4'] and head_token != tok:
            continue

        elif tok['xpos'] in ['Б3', 'Б4'] and head_token != tok:
            child_tokens_array = get_child_recursive_with_rebinding_part_b1_BSP(tok, sentence, child_tokens_array, exception_array)

        if tok['head'] == head_token['id']:
            if tok not in exception_array and tok['xpos'] != 'Б2':
                child_tokens_array.append(tok)
                child_tokens_array = get_child_recursive_with_rebinding_part_b1_BSP(tok, sentence, child_tokens_array, exception_array)

    return child_tokens_array


#Проверка на то, должна ли выделяться эта часть по Б2
def is_b2(token):
    if token['form'] is None:
        return 0
    if (token['lemma'] in ['КАК', 'ГДЕ', 'КОГДА', 'КУДА', 'ОТКУДА', 'ПОЧЕМУ'] and token['upos'] == 'ADV') or \
    token['lemma'] in ['КОТОРЫЙ', 'КАКОЙ', 'КАКОВ', 'ЧЕЙ', 'СКОЛЬКО'] or (token['form'].upper() in ['ЧТО', 'КТО']
                and token['upos'] != 'CCONJ'):
        return 1
    return 0

#Выделение частей БСП в СГ по Б1
def rule_b_1_BSP(sentence: TokenList) -> bool:
    bool_new_group = False
    text_group = ''
    head_tokens_list = []
    head_token_childs_list = []
    good_deprels = ['сент-соч', 'разъяснит', 'вводн', 'изъясн']

    for token in sentence:
        if token['form'] is None:
            continue

        if token['deprel'] in good_deprels:
            if token['upos'] == 'VERB':
                if get_head(token, sentence)['xpos'] == 'Б2':
                    continue

                head_tokens_list.append(token)
                tokens_head = get_head(token, sentence)
                if tokens_head['deprel'] == 'предик':
                    tokens_head = get_head(tokens_head, sentence)
                    head_tokens_list.append(tokens_head)
            else:
                for child_token in get_one_step_children_token(token, sentence):
                    if is_b2(child_token):
                        continue

                    elif child_token['upos'] == 'ADP' and len(get_one_step_children_token(child_token, sentence)) == 1:
                        if is_b2(get_one_step_children_token(child_token, sentence)[0]):
                            continue

                    elif child_token['deprel'] == 'предик':
                        if get_head(token, sentence)['xpos'] == 'Б2':
                            continue

                        head_tokens_list.append(token)
                        tokens_head = get_head(token, sentence)
                        if tokens_head['deprel'] == 'предик':
                            tokens_head = get_head(tokens_head, sentence)
                            head_tokens_list.append(tokens_head)
                        break

    for head_token in head_tokens_list:
        head_token_childs_list = get_child_recursive_with_rebinding_part_b1_BSP(head_token, sentence, head_token_childs_list, head_tokens_list)
        head_token_childs_list.append(head_token)

        buf_head_token_childs_list = head_token_childs_list.copy()
        for t in head_token_childs_list:
            if t['lemma'] == '_':
                buf_head_token_childs_list.remove(t)
                components_sg = get_group_all_component_sg(t, sentence)
                for cmp in components_sg:
                    if cmp not in buf_head_token_childs_list:
                        buf_head_token_childs_list.append(cmp)

        buf_head_token_childs_list.sort(key=lambda token: token['id'])
        for t in buf_head_token_childs_list:
            text_group += t['form'] + ' '
        text_group = text_group[:-1]

        new_token = create_sg(len(sentence) + 1, text_group, 'Б1', head_token['head'], head_token['deprel'])
        sentence.append(new_token)

        text_group = ''
        bool_new_group = True
        head_token['deprel'] = '_'
        head_token['head'] = len(sentence)

        for reb_token in head_token_childs_list:
            cur_children_token = get_one_step_children_token(reb_token, sentence)
            for t in cur_children_token:
                if t not in head_token_childs_list:
                    t['head'] = len(sentence)

        head_token_childs_list = []

    return bool_new_group
