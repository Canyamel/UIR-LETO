from proc.proc_conllu import *

#обработка латиницы, выделяемой по Б4
def rule_b_4_eng(sentence: TokenList) -> bool:
    flag = 1
    eng_big_letters = 'ABCDEFGHIGKNLMOPQRSTUVWXYZ'
    rus_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    bool_new_group = False
    arr_of_sg_tokens = []
    stri = ''
    head_tokens_list = []
    text_group = ''

    for search_token in sentence:
        if search_token['form'] is None:
            continue

        if len(search_token['form'].split()) > 1 and search_token['form'].split()[-1]!='-':
            continue

        for i in search_token['form']:
            if i.upper() in rus_letters:
                flag = 1
                break

            if i in eng_big_letters and flag:
                flag = 0
                head_tokens_list.append(search_token)
                break

    for head_token in head_tokens_list:
        stri += head_token['form'] + ' '

    for head_token in head_tokens_list:
        text_group += head_token['form'] + ' '
        arr_of_sg_tokens.append(head_token)
        prev_token = head_token
        flag = 1

        for current_token in sentence[head_token['id']:]:
            if current_token['form'] is None:
                continue

            if current_token['deprel'] == 'аппоз' and current_token['head'] == prev_token['id'] and flag == 1:
                if len(current_token['form']) == 1:
                    if current_token['form'].upper() in eng_big_letters:
                        text_group += current_token['form'] + ' '
                        arr_of_sg_tokens.append(current_token)
                    else:
                        flag = 0
                        break
                else:
                    #print(current_token['form'])
                    if current_token['form'][0].upper() not in eng_big_letters:
                        flag = 0
                        break

                    elif current_token['form'][-1] in ')",-':
                        text_group += current_token['form'] + ' '
                        arr_of_sg_tokens.append(current_token)
                        flag = 0
                        break

                    elif current_token['form'][0].upper() in eng_big_letters:
                        text_group += current_token['form']+' '
                        arr_of_sg_tokens.append(current_token)

                    elif current_token['form'][0] in '("' and current_token['form'][1].upper() in eng_big_letters:
                        text_group += current_token['form']+' '
                        arr_of_sg_tokens.append(current_token)

                    else:
                        flag = 0
                        break
            else:
                break
            prev_token = current_token
        if (len(text_group.split()) > 1 and text_group.split()[-1] != '-') or (len(text_group.split()) > 2) and flag == 0 \
                and '?' not in text_group:

            new_token = create_sg(len(sentence) + 1, text_group, 'Б4', head_token['head'], head_token['deprel'])
            sentence.append(new_token)
            bool_new_group = True
            flag = 1
            head_token['deprel'] = '_'
            head_token['head'] = len(sentence)

            #for re_token in get_children(head_token, sentence):
            #    if re_token['deprel'] != 'аппоз':
            #        rebind_tokens(new_token, re_token)

            # Момент с перепривязкой нижележащих токенов
            for reb_token in arr_of_sg_tokens:
                if reb_token == head_token:
                    reb_token['deprel'] = '_'
                cur_children_token = get_one_step_children_token(reb_token, sentence)
                for t in cur_children_token:
                    if t not in arr_of_sg_tokens:
                        t['head'] = len(sentence)

        text_group = ''
        arr_of_sg_tokens = []

    return bool_new_group


#обработка кириллицы, выделяемой по Б4
def rule_b_4_rus(sentence: TokenList) -> bool:
    flag = 1
    eng_big_letters = 'ABCDEFGHIJKNLMOPQRSTUVWXYZ'
    rus_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    bool_new_group = False
    stri = ''
    arr_of_sg_tokens = []
    #for token in sentence:
    #    stri += token['form']+' '
    #for k in eng_big_letters:
    #    if k in stri:
    #        saved_size = 1
    head_tokens_list = []
    text_group = ''
    for search_token in sentence:
        if search_token['form'] is None:
            continue

        if (len(search_token['form'].split())) > 1 and search_token['form'].split() != '-' or len(search_token['form'].split()) > 2:
            continue

        for i in search_token['form']:
            if i in rus_letters:
                if search_token['form'] == search_token['form'].upper():
                    head_tokens_list.append(search_token)
                    break
                elif flag:
                    flag = 0
                    head_tokens_list.append(search_token)
                    break
                else:
                    break
            if i in eng_big_letters.lower()+rus_letters.lower()+'-':
                flag = 1
                break

    for head_token in head_tokens_list:
        stri += head_token['form'] + ','

    for head_token in head_tokens_list:
        text_group += head_token['form'] + ' '
        arr_of_sg_tokens.append(head_token)
        prev_token = head_token
        flag = 1
        for current_token in sentence[head_token['id']:]:
            if current_token['form'] is None:
                continue

            if current_token['deprel'] == 'аппоз' and current_token['head'] == prev_token['id'] and flag == 1:
                if len(current_token['form']) == 1:
                    if current_token['form'][0].upper() in rus_letters + '0123456789':
                        text_group += current_token['form']+' '
                        arr_of_sg_tokens.append(current_token)
                    else:
                        flag = 0
                        break
                else:
                    if current_token['form'][0].upper() in rus_letters + '0123456789':
                        text_group += current_token['form']+' '
                        arr_of_sg_tokens.append(current_token)
                        if current_token['form'][-1] in ';,)':
                            flag = 0
                            break
                    else:
                        flag = 0
                        break
                if current_token == sentence[-1]:
                    flag = 0
                    break
            else:
                flag = 0
                break
            prev_token = current_token

        if (len(text_group.split()) > 1 and text_group.split()[-1] != '-') or (len(text_group.split()) > 2) and flag == 0:

            new_token = create_sg(len(sentence) + 1, text_group, 'Б4', head_token['head'], head_token['deprel'])
            sentence.append(new_token)
            bool_new_group = True
            flag = 1
            head_token['deprel'] = '_'
            head_token['head'] = len(sentence)

            #for re_token in get_children(head_token, sentence):
            #    if re_token['deprel'] != 'аппоз':
            #        rebind_tokens(new_token, re_token)

            # Момент с перепривязкой нижележащих токенов
            for reb_token in arr_of_sg_tokens:
                cur_children_token = get_one_step_children_token(reb_token, sentence)
                for t in cur_children_token:
                    if t not in arr_of_sg_tokens:
                        t['head'] = len(sentence)

        text_group = ''
        arr_of_sg_tokens = []

    return bool_new_group



#комбинирование латиницы и кириллицы в одну функцию
def rule_b_4(sentence):
    bool_new_group = False
    bool_new_group += rule_b_4_eng(sentence)
    bool_new_group += rule_b_4_rus(sentence)
    return bool_new_group