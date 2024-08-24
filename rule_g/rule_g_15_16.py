from proc.proc_conllu import *

def rule_g_15_16(sentence: TokenList) -> bool:
    # Поиск всех потенциальные групп слов (в том числе и единичные группы), которые связаны с остальным предложением отношением ВВОДН
    introductory_groups = []
    for token in sentence:
        bool_new_group = False
        group = []
        if token['deprel'] == 'вводн' and token['lemma'] != '_':
            if sentence[token['head'] - 1]['xpos'] not in ['Г15', 'Г16']:
                group = [token]
                group.extend(get_children_token(token, sentence))
                introductory_groups.append(group)

    # Разделить группы на две части, которые выполняют условие Г15 и которые выполняют условие Г16
    introductory_groups_15 = []
    introductory_groups_16 = []
    for group in introductory_groups:
        bool_15 = True
        bool_16 = True
        cnt_imen_padej = 0
        cnt_live = 0
        for token in group:
            if check_feat(token, 'ОД'):
                cnt_live += 1
            if check_feat(token, 'ИМ'):
                cnt_imen_padej += 1
            if token['deprel'] in ['предик']:
                bool_15 = False
                bool_16 = False
                continue
            if token['deprel'] in ['аппоз', 'об-аппоз']:
                bool_15 = False
            if not check_feat(token, 'ИМ') or check_feat(token, 'ЗВ'):
                bool_16 = False
            if token['upos'] in ['VERB', 'ADV']:
                bool_16 = False
            if token['upos'] in ['ADJ'] and len(group) == 1:
                bool_15 = False
        if cnt_imen_padej == len(group) and cnt_live > 1:
            bool_15 = False

        if bool_15:
            bool_new_group = True
            introductory_groups_15.append(group)
        elif bool_16:
            bool_new_group = True
            introductory_groups_16.append(group)

    # Создание новых групп
    if bool_new_group:
        id_new_group = len(sentence) + 1

        check_group_15 = []
        for group in introductory_groups_15:
            for token in group:
                check_group_15.append(token)
        check_group_16 = []
        for group in introductory_groups_16:
            for token in group:
                check_group_16.append(token)

        # Выделение групп Г15
        group = []
        if introductory_groups_15 != []:
            for token in sentence:
                if token['head'] == 1:
                    token['head'] = id_new_group
                if token not in check_group_15 and token['form'] != '_':
                    group.append(token)

            phrase = ''
            group.sort(key=lambda token: token['id'])
            for token in group:
                phrase += token['form'] + ' '
            phrase = phrase[:-1]
            sentence.append(create_sg(id_new_group, phrase, 'Г15', 1, '_'))
            id_15_group = len(sentence)

            for introductory_group in introductory_groups_15:
                if len(introductory_group) > 1:
                    head_token = None
                    for token in introductory_group:
                        if token['deprel'] == 'вводн':
                            head_token = token
                    introductory_group.sort(key=lambda token: token['id'])
                    head_token['deprel'] = '_'
                    head_token['head'] = len(sentence) + 1
                    phrase = ""
                    for token in introductory_group:
                        phrase += token['form'] + ' '
                    phrase = phrase[:-1]
                    sentence.append(create_sg(len(sentence) + 1, phrase, 'Г15', id_new_group, 'вводн'))
                    head_token['head'] = len(sentence)
                else:
                    introductory_group[0]['head'] = id_new_group

        # Выделение групп Г16
        group = []
        if introductory_groups_16 != []:
            if introductory_groups_15 != []:
                for token in sentence:
                    if token['head'] == id_new_group and token['deprel'] == '_':
                        token['head'] = len(sentence) + 1
                    if token not in check_group_16 and token not in check_group_15 and token['form'] != '_':
                        group.append(token)
                id_new_group = len(sentence) + 1
            else:
                for token in sentence:
                    if token['head'] == 1:
                            token['head'] = id_new_group
                    if token not in check_group_16 and token not in check_group_15 and token['form'] != '_':
                        group.append(token)

            phrase = ''
            group.sort(key=lambda token: token['id'])
            for token in group:
                phrase += token['form'] + ' '
            phrase = phrase[:-1]
            if introductory_groups_15 != []:
                sentence.append(create_sg(id_new_group, phrase, 'Г16', id_15_group, '_'))
            else:
                sentence.append(create_sg(id_new_group, phrase, 'Г16', 1, '_'))

            for introductory_group in introductory_groups_16:
                if len(introductory_group) > 1:
                    head_token = None
                    for token in introductory_group:
                        if token['deprel'] == 'вводн':
                            head_token = token
                    introductory_group.sort(key=lambda token: token['id'])
                    head_token['deprel'] = '_'
                    head_token['head'] = len(sentence) + 1
                    phrase = ""
                    for token in introductory_group:
                        phrase += token['form'] + ' '
                    phrase = phrase[:-1]
                    sentence.append(create_sg(len(sentence) + 1, phrase, 'Г16', id_new_group, 'вводн'))
                    head_token['head'] = len(sentence)
                else:
                    introductory_group[0]['head'] = id_new_group

    return bool_new_group