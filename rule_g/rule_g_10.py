from proc.proc_conllu import *

def rule_g_10(sentence: TokenList) -> bool:
    bool_new_group = False
    groups = []
    for token in sentence:
        if token['upos'] == 'VERB':
            group = []
            children = get_one_step_children_token(token, sentence)
            group.append(token)

            if 'НЕСОВ' in str(token['feats']):
                for child in children:
                    if child['upos'] == 'NOUN' and ('ТВОР' in str(child['feats']) or 'ВИН' in str(child['feats']) or 'ДАТ' in str(child['feats'])):
                        group.append(child)

                    if '_' in child['xpos']:
                        children_of_group = get_one_step_children_token(child, sentence)
                        for child_of_group in children_of_group:
                            if child_of_group['upos'] == 'NOUN' and ('ТВОР' in str(child_of_group['feats']) or 'ВИН' in str(child_of_group['feats']) or 'ДАТ' in str(child_of_group['feats'])):
                                group.append(child)

                    if child['upos'] == 'ADP':
                        children_of_adp = get_one_step_children_token(child, sentence)
                        for child_adp in children_of_adp:
                            if child_adp['upos'] == 'NOUN' and ('ТВОР' in str(child_adp['feats']) or 'ВИН' in str(child_adp['feats']) or 'ДАТ' in str(child['feats'])):
                                group.append(child)
                                group.append(child_adp)

                            if '_' in child_adp['xpos']:
                                children_of_group = get_one_step_children_token(child_adp, sentence)
                                for child_of_group in children_of_group:
                                    if child_of_group['upos'] == 'NOUN' and ('ТВОР' in str(child_of_group['feats']) or 'ВИН' in str(child_of_group['feats']) or 'ДАТ' in str(child_of_group['feats'])):
                                        group.append(child_adp)

            if group not in groups and len(group) > 1:
                if group not in groups:
                    groups.append(group)

    if len(groups) > 0:
        bool_new_group = True
        for group in groups:
            if len(group) > 1:
                group_id = []
                for token in group:
                    group_id.append(token['id'])
                ordered_id = sorted(group_id)

                text = ''
                for i in range(len(ordered_id)):
                    text = text + sentence[ordered_id[i]-1]['form'] + ' '
                max_id = -1
                for i in range(len(ordered_id)):
                    if sentence[ordered_id[i]-1]['head'] not in ordered_id:
                        max_id = ordered_id[i]
                token = sentence[max_id-1]

                # Получить все слова, которые связаны со словами из группы
                list_one_step_children_token = []
                for t in group:
                    list_one_step_children_token.extend(get_one_step_children_token(t, sentence))

                # Добавить новую группу и изменить связи между элементами ССГ
                for t in list_one_step_children_token:
                    if t not in group:
                        t['head'] = len(sentence) + 1

                sentence.append(create_sg(len(sentence) + 1, text, 'Г10', sentence[max_id-1]['head'], sentence[max_id-1]['deprel']))
                token['head'] = len(sentence)
                token['deprel'] = '_'

    return bool_new_group