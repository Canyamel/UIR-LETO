from proc.proc_conllu import *

def rule_g_6(sentence: TokenList) -> bool:
    bool_new_group = False
    for token in sentence:
        # поиск ГЛ, который не является ИНФ
        if token['upos'] == 'VERB' and not check_feat(token, 'ИНФ'):
            head_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1:
                head_token = sentence[head_token['head'] - 1]

            if head_token['xpos'] != 'Г6' or sentence[token['head'] - 1]['xpos'] != 'Г6' and head_token['deprel'] == '_':
                # поиск N, который зависит от найденного слова
                for token in get_one_step_children_token(head_token, sentence):
                    buf_token = token
                    if buf_token['lemma'] == '_' and buf_token['form'] == '_':
                        root_component = get_root_component_sg(buf_token, sentence)
                        if root_component != None:
                            buf_token = get_root_component_sg(buf_token, sentence)
                    if buf_token['upos'] in ['PRON', 'NOUN', 'ADJ', 'ADV']:
                        noun_token = token

                        # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                        pairs = get_sorted_pairs(sentence)
                        noun_pairs = []
                        id_child_token = None
                        buf_pairs = pairs.copy()
                        if noun_token['lemma'] == '_' and noun_token['form'] == '_':
                            id_noun_token = get_root_component_sg(noun_token, sentence)['id']
                            for token in sentence:
                                if token['head'] == id_noun_token:
                                    id_child_token = token['id']
                                    break
                            for pair in buf_pairs:
                                if id_noun_token in pair and get_id_head_token(noun_token, sentence) not in pair and id_child_token not in pair:
                                    noun_pairs.append(pair)
                                    pairs.remove(pair)
                        else:
                            id_noun_token = noun_token['id']
                            for pair in buf_pairs:
                                if id_noun_token in pair and get_id_head_token(noun_token, sentence) not in pair:
                                    noun_pairs.append(pair)
                                    pairs.remove(pair)

                        # Проверить, что существуют пары с ИНФ
                        qnt_noun_pairs = len(noun_pairs)
                        if qnt_noun_pairs > 0:
                            # Удалить все пары с ИНФ, которые нарушают проективность
                            buf_noun_pairs = noun_pairs.copy()
                            for noun_pair in buf_noun_pairs:
                                if get_id_head_token(noun_token, sentence) > noun_pair[0] and get_id_head_token(noun_token, sentence) < noun_pair[1]:
                                    noun_pairs.remove(noun_pair)
                                    continue
                                for pair in pairs:
                                    if (noun_pair[0] > pair[0] and noun_pair[0] < pair[1] and (noun_pair[1] < pair[0] or noun_pair[1] > pair[1])) or (noun_pair[1] > pair[0] and noun_pair[1] < pair[1] and (noun_pair[0] < pair[0] or noun_pair[0] > pair[1])):
                                        noun_pairs.remove(noun_pair)
                                        break

                            # Проверка, что нужно добавлять новую группу
                            if qnt_noun_pairs > len(noun_pairs):
                                bool_new_group = True

                                # Получить набор слов, которые образуют новую группу
                                group_token = [head_token, noun_token]
                                # for pair in noun_pairs:
                                #     if pair[0] != noun_token['id']:
                                #         token = sentence[pair[0] - 1]
                                #     else:
                                #         token = sentence[pair[1] - 1]
                                #     group_token.extend(get_token_for_group(token, sentence))

                                # Получить словосочетание
                                buf_group_token = group_token.copy()
                                for token in buf_group_token:
                                    if token['lemma'] == '_' and token['form'] == '_':
                                        group_token.remove(token)
                                        group_token.extend(get_group_component_sg(token, sentence))
                                group_token.sort(key=lambda token: token['id'])
                                phrase = ''
                                for token in group_token:
                                    phrase += token['form'] + ' '
                                phrase = phrase[:-1]
                                group_token = buf_group_token.copy()

                                # Получить все слова, которые связаны со словами из группы
                                group_one_step_child_token = []
                                for token in group_token:
                                    group_one_step_child_token.extend(get_one_step_children_token(token, sentence))

                                # Добавить новую группу и изменить связи между элементами ССГ
                                for token in group_one_step_child_token:
                                    if token not in group_token:
                                        token['head'] = len(sentence) + 1
                                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г6', head_token['head'], head_token['deprel']))
                                head_token['deprel'] = '_'
                                head_token['head'] = len(sentence)

        # Поиск ИНФ, который не завист от другого ИНФ
        if check_feat(token, 'ИНФ') and not check_feat(sentence[token['head'] - 1], 'ИНФ'):
            head_token = token
            last_inf_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1:
                head_token = sentence[head_token['head'] - 1]

            group_token = [head_token]
            inf_group_token = [head_token]
            bool_N = False
            while True:
                if head_token['head'] == 1:
                    break

                buf_head_token = sentence[head_token['head'] - 1]

                if buf_head_token['xpos'] in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                    break

                if buf_head_token['deprel'] in ['сент-соч', 'кратн', 'релят', 'разъяснит', 'примыкат', 'подч-союзн', 'инф-союзн', 'сравн-союзн', 'сравнит', 'эксплет']:
                    break

                if buf_head_token['lemma'] == '_' and buf_head_token['form'] == '_':
                    buf_head_token = get_root_component_sg(buf_head_token, sentence)

                if buf_head_token['id'] > head_token['id']:
                    break

                if buf_head_token['upos'] in ['VERB', 'NOUN', 'ADJ', 'ADV']:
                    if buf_head_token['upos'] in ['NOUN', 'ADJ', 'ADV']:
                        if bool_N:
                            break
                        bool_N = True
                    head_token = sentence[head_token['head'] - 1]
                    group_token.append(head_token)
                else:
                    break

            if head_token['xpos'] != 'Г6' or sentence[token['head'] - 1]['xpos'] != 'Г6' and head_token['deprel'] == '_':
                # Поиск всех зависимых ИНФ от найденного ИНФ
                bool_inf_child = True
                while bool_inf_child:
                    bool_inf_child = False
                    for token in sentence:
                        if token['head'] == last_inf_token['id']:
                            if check_feat(token, 'ИНФ'):
                                group_token.append(token)
                                inf_group_token.append(token)
                                last_inf_token = token
                                bool_inf_child = True
                                break

                bool_noun = False
                for noun_token in get_children_token(last_inf_token, sentence):
                    bool_noun = False
                    if noun_token['lemma'] == '_' and noun_token['form'] == '_':
                        if get_root_component_sg(noun_token, sentence)['upos'] in ['NOUN', 'ADJ', 'ADV']:
                            bool_noun = True
                    else:
                        if noun_token['upos'] in ['NOUN', 'ADJ', 'ADV']:
                            bool_noun = True

                if bool_noun:
                    group_token.append(noun_token)

                    # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                    pairs = get_sorted_pairs(sentence)
                    buf_pairs = pairs.copy()
                    noun_pairs = []
                    for pair in buf_pairs:
                        if noun_token['id'] in pair and noun_token['head'] not in pair:
                            noun_pairs.append(pair)
                            pairs.remove(pair)

                    # Удалить все пары с СУЩ, которые нарушают проективность
                    qnt_noun_pairs = len(noun_pairs)
                    buf_noun_pairs = noun_pairs.copy()
                    for noun_pair in buf_noun_pairs:
                        if noun_token['head'] > noun_pair[0] and noun_token['head'] < noun_pair[1]:
                            noun_pairs.remove(noun_pair)
                            continue
                        for pair in pairs:
                            if (noun_pair[0] > pair[0] and noun_pair[0] < pair[1] and (noun_pair[1] < pair[0] or noun_pair[1] > pair[1])) or (noun_pair[1] > pair[0] and noun_pair[1] < pair[1] and (noun_pair[0] < pair[0] or noun_pair[0] > pair[1])):
                                noun_pairs.remove(noun_pair)
                                break

                    # Проверка, что нужно добавлять новую группу
                    if qnt_noun_pairs > len(noun_pairs):
                        bool_new_group = True

                        # Дополнить набор слов, которые образуют новую группу
                        # for pair in noun_pairs:
                        #     if pair[0] != noun_token['id']:
                        #         token = sentence[pair[0] - 1]
                        #     else:
                        #         token = sentence[pair[1] - 1]
                        #     group_token.extend(get_token_for_group(token, sentence))

                        # Получить текст группы
                        buf_group_token = group_token.copy()
                        for token in buf_group_token:
                            if token['lemma'] == '_' and token['form'] == '_':
                                group_token.remove(token)
                                group_token.extend(get_group_component_sg(token, sentence))
                        group_token.sort(key=lambda token: token['id'])
                        phrase = ''
                        for token in group_token:
                            phrase += token['form'] + ' '
                        phrase = phrase[:-1]
                        group_token = buf_group_token.copy()

                        # Получить все слова, которые связаны со словами из группы
                        list_one_step_children_token = []
                        for token in group_token:
                            list_one_step_children_token.extend(get_one_step_children_token(token, sentence))

                        # Добавить новую группу и изменить связи между элементами ССГ
                        for token in list_one_step_children_token:
                            if token not in group_token:
                                token['head'] = len(sentence) + 1
                        sentence.append(create_sg(len(sentence) + 1, phrase, 'Г6', head_token['head'], head_token['deprel']))
                        head_token['deprel'] = '_'
                        head_token['head'] = len(sentence)
    return bool_new_group