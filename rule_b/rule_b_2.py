from proc.proc_conllu import *

#Выделение токенов, составляющих СГ по Б2
def get_child_recursive_with_rebinding_part_b2(head_token, sentence, child_tokens_array, exception_array):
    for tok in sentence:
        if tok['form'] is None:
            continue

        if tok['head'] == head_token['id']:
            if tok not in exception_array and tok['deprel'] not in ['разъяснит', 'вводн']:
                if tok['upos'] == 'CCONJ' and sentence[takeIdToken(tok)-2]['form'][-1] == ',' or \
                        tok['upos'] == 'PART' and sentence[takeIdToken(tok)-3]['form'][-1] == ',':
                    continue

                else:
                    child_tokens_array.insert(0, tok)
                if tok['form'][-1] == ':':
                    continue

                else:
                    child_tokens_array = get_child_recursive_with_rebinding_part_b2(tok, sentence, child_tokens_array, exception_array)

    return child_tokens_array

#проверка, что это часть выделяется по Б2
def is_b2(token):
    if token['form'] is None:
        return False

    if (token['lemma'] in ['КАК', 'ГДЕ', 'КОГДА', 'КУДА', 'ОТКУДА', 'ПОЧЕМУ'] and token['upos'] == 'ADV') or \
    token['lemma'] in ['КОТОРЫЙ', 'КАКОЙ', 'КАКОВ', 'ЧЕЙ', 'СКОЛЬКО'] or (token['form'].upper() in ['ЧТО', 'КТО']
                and token['upos'] != 'CCONJ'):
        return True
    return  False


#Нахождение корней частей, которые не должны входить в Б2
def find_except_words(sentence: TokenList):
    good_deprels = ['сент-соч', 'разъяснит', 'вводн', 'изъясн']
    good_podch_deprels = ['эксплет', 'сент-соч', 'изъясн', 'сравнит', 'предик', 'вводн', 'обст', '1-компл', '2-компл',
                            '3-компл', '4-компл', '1-несобст-компл', '1-несобст-компл', '2-несобст-компл',
                            '3-несобст-компл', '4-несобст-компл', 'атриб',
                            'об-копр', 'суб-копр']
    except_tokens_list = []
    for token in sentence:
        if token['form'] is None:
            continue

        if token['deprel'] in good_deprels:
            if token['upos'] == 'VERB':
                if get_head(token, sentence)['xpos'] == 'Б2':
                    continue

                except_tokens_list.append(token)
                tokens_head = get_head(token, sentence)
                if tokens_head['deprel'] == 'предик':
                    tokens_head = get_head(tokens_head, sentence)
                    except_tokens_list.append(tokens_head)
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

                        except_tokens_list.append(token)
                        tokens_head = get_head(token, sentence)
                        if tokens_head['deprel']=='предик':
                            tokens_head = get_head(tokens_head, sentence)
                            except_tokens_list.append(tokens_head)
                        break

        if token['deprel'] in ('подч-союзн', 'сравн-союзн') and get_head(token, sentence)['upos'] == 'CCONJ' and \
                get_head(token, sentence)['id'] not in get_all_id(except_tokens_list):

            except_tokens_list.append(get_head(token, sentence))
        elif token['deprel'] in good_podch_deprels and token['upos'] == 'CCONJ' and token['id'] not in get_all_id(except_tokens_list):
            except_tokens_list.append(token)

    return except_tokens_list


def rule_b_2(sentence: TokenList) -> bool:
    bool_new_group = False
    text_group = ''
    head_tokens_list = []
    for token in sentence:
        if token['form'] is None:
            continue

        if (token['lemma'] in ['КАК', 'ГДЕ', 'КОГДА', 'КУДА', 'ОТКУДА', 'ПОЧЕМУ'] and token['upos'] == 'ADV') or \
                token['lemma'] in ['КОТОРЫЙ', 'КАКОЙ', 'КАКОВ', 'ЧЕЙ', 'СКОЛЬКО'] or (token['form'].upper() in ['ЧТО','КТО'] and token['upos'] != 'CCONJ'):
            if sentence[takeIdToken(token)-2]['form'][-1] in ':,' and token['head'] != 1:
                head_token = token

            elif sentence[takeIdToken(token)-2]['upos'] == 'ADP' and sentence[takeIdToken(token)-3]['form'][-1] in ',:' and token['head'] != 1:
                head_token = get_head(token, sentence)

            else:
                break

            if head_token['upos'] == token['upos'] and token['deprel']=='сочин':
                break

            flag = 1
            while head_token['head'] != 1 and flag:
                if takeIdToken(head_token) < takeIdToken(get_head(head_token,sentence)):
                    head_token = get_head(head_token, sentence)
                else:
                    flag = 0

            head_tokens_list.append(head_token)
            head_token_childs_list = []

    except_tokens_list = find_except_words(sentence)
    for head_token in head_tokens_list:
        head_token_childs_list = get_child_recursive_with_rebinding_part_b2(head_token, sentence, head_token_childs_list, head_tokens_list + except_tokens_list)
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

        new_token = create_sg(len(sentence) + 1, text_group, 'Б2', head_token['head'], head_token['deprel'])
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

        #проверка и перепривязка при наличии разъяснит и вводн связей и союзных подчинительных
        #for some_token in get_one_step_children_token(head_token, sentence):
        #    if some_token['form'] is None:
        #        continue

        #    if some_token['deprel'] in ['разъяснит', 'вводн']:
        #        some_token = len(sentence)

        #    if some_token['upos'] == 'CCONJ':
        #        if some_token['deprel'] == 'сочин' and len(get_one_step_children_token(some_token, sentence)) == 1 and get_head(some_token, sentence)['upos'] == get_one_step_children_token(some_token, sentence)[0]['upos'] and get_head(some_token, sentence)['upos']!='VERB':
        #            continue
        #        else:
        #            some_token = len(sentence)

    return bool_new_group