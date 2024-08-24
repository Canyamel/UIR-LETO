from proc.proc_conllu import *

def rule_g_3(sentence: TokenList) -> bool:
    bool_new_group = False
    for token in sentence:
        # поиск ГЛ, который не является ИНФ
        if token['upos'] == 'VERB' and not check_feat(token, 'ИНФ'):
            head_token = token
            while head_token['deprel'] == '_' and head_token['head'] != 1 and sentence[head_token['head'] - 1]['xpos'] not in ['Г15', 'Г16']:
                head_token = sentence[head_token['head'] - 1]

            if head_token['xpos'] != 'Г3' or sentence[token['head'] - 1]['xpos'] != 'Г3' and head_token['deprel'] == '_':
                # поиск ИНФ, который зависит от найденного слова
                for token in get_one_step_children_token(head_token, sentence):
                    buf_token = token
                    if buf_token['lemma'] == '_' and buf_token['form'] == '_' and buf_token['xpos'] not in ['Г3', 'Г4', 'Г5', 'Г6', 'Г7', 'Г8', 'Г15', 'Г16']:
                        buf_token = get_root_component_sg(buf_token, sentence)
                    if  check_feat(buf_token, 'ИНФ'):
                        inf_token = token

                        # Поиск двух наборов пар связей (в первой все связи, в которых отсуствует найденный СУЩ, а во второй - присуствует)
                        pairs = get_sorted_pairs(sentence)
                        inf_pairs = []
                        buf_pairs = pairs.copy()
                        if inf_token['lemma'] == '_' and inf_token['form'] == '_':
                            id_inf_token = get_root_component_sg(inf_token, sentence)['id']
                            id_child_token = None
                            for token in sentence:
                                if token['head'] == id_inf_token:
                                    id_child_token = token['id']
                                    break
                            for pair in buf_pairs:
                                if id_child_token != None:
                                    if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair and id_child_token not in pair:
                                        inf_pairs.append(pair)
                                        pairs.remove(pair)
                        else:
                            id_inf_token = inf_token['id']
                            for pair in buf_pairs:
                                if id_inf_token in pair and get_id_head_token(inf_token, sentence) not in pair:
                                    inf_pairs.append(pair)
                                    pairs.remove(pair)

                        # Проверить, что существуют пары с ИНФ
                        qnt_inf_pairs = len(inf_pairs)
                        if qnt_inf_pairs > 0:

                            # Удалить все пары с ИНФ, которые нарушают проективность
                            buf_inf_pairs = inf_pairs.copy()
                            for inf_pair in buf_inf_pairs:
                                if get_id_head_token(inf_token, sentence) > inf_pair[0] and get_id_head_token(inf_token, sentence) < inf_pair[1]:
                                    inf_pairs.remove(inf_pair)
                                    continue
                                for pair in pairs:
                                    if (inf_pair[0] > pair[0] and inf_pair[0] < pair[1] and (inf_pair[1] < pair[0] or inf_pair[1] > pair[1])) or (inf_pair[1] > pair[0] and inf_pair[1] < pair[1] and (inf_pair[0] < pair[0] or inf_pair[0] > pair[1])):
                                        inf_pairs.remove(inf_pair)
                                        break

                            # Проверка, что нужно добавлять новую группу
                            if qnt_inf_pairs > len(inf_pairs):
                                bool_new_group = True

                                # Получить набор слов, которые образуют новую группу
                                group_token = [head_token, inf_token]
                                # for pair in inf_pairs:
                                #     if pair[0] != inf_token['id']:
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
                                    for child_token in get_one_step_children_token(token, sentence):
                                        if child_token not in group_token:
                                            group_one_step_child_token.extend(get_one_step_children_token(token, sentence))

                                # Добавить новую группу и изменить связи между элементами ССГ
                                for token in group_one_step_child_token:
                                    if token not in group_token:
                                        token['head'] = len(sentence) + 1
                                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г3', head_token['head'], head_token['deprel']))
                                head_token['deprel'] = '_'
                                head_token['head'] = len(sentence)

    return bool_new_group