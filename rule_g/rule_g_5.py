from proc.proc_conllu import *

def rule_g_5(sentence: TokenList) -> bool:
    bool_new_group = False
    for token in sentence:
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
                    if buf_head_token == None:
                        break

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

            if head_token['xpos'] != 'Г5' or sentence[token['head'] - 1]['xpos'] != 'Г5' and head_token['deprel'] == '_':
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

                bool_check_g5 = True
                if len(group_token) == 2:
                    for token in group_token:
                        if not check_feat(token, 'ИНФ'):
                            bool_check_g5 = False
                if len(group_token) < 2:
                    bool_check_g5 = False

                if bool_check_g5:
                    # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует последний ИНФ, а во второй - присуствует)
                    pairs = get_sorted_pairs(sentence)
                    buf_pairs = pairs.copy()
                    inf_pairs = []
                    for pair in buf_pairs:
                        if last_inf_token['id'] in pair and last_inf_token['head'] not in pair:
                            inf_pairs.append(pair)
                            pairs.remove(pair)

                    # Удалить все пары с последним ИНФ, которые нарушают проективность
                    qnt_inf_pairs = len(inf_pairs)
                    buf_inf_pairs = inf_pairs.copy()
                    for inf_pair in buf_inf_pairs:
                        if last_inf_token['head'] > inf_pair[0] and last_inf_token['head'] < inf_pair[1]:
                            inf_pairs.remove(inf_pair)
                            continue
                        for pair in pairs:
                            if (inf_pair[0] > pair[0] and inf_pair[0] < pair[1] and (inf_pair[1] < pair[0] or inf_pair[1] > pair[1])) or (inf_pair[1] > pair[0] and inf_pair[1] < pair[1] and (inf_pair[0] < pair[0] or inf_pair[0] > pair[1])):
                                inf_pairs.remove(inf_pair)
                                break

                    # Проверка, что нужно добавлять новую группу
                    if qnt_inf_pairs > len(inf_pairs):
                        bool_new_group = True

                        # Дополнить набор слов, которые образуют новую группу
                        # for pair in inf_pairs:
                        #     if pair[0] != last_inf_token['id']:
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
                        sentence.append(create_sg(len(sentence) + 1, phrase, 'Г5', head_token['head'], head_token['deprel']))
                        head_token['deprel'] = '_'
                        head_token['head'] = len(sentence)
    return bool_new_group