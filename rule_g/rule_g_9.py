from proc.proc_conllu import *

def rule_g_9(sentence: TokenList) -> bool:
    bool_new_group = False
    groups = []
    mest = [
            'МЕНЯ','НАС','ТЕБЯ','ВАС','ЕЕ','ЕЙ','ЕЁ','ИХ',
            'МНЕ','ТЕБЕ','ВАМ','ЕМУ','ЕЁ','ИМ',
            'МЕНЯ','НАС','ВАС','ЕГО',
            'НАМИ','ТОБОЙ','ВАМИ','ЕЮ','ИМИ', 'СЕЙ',
            'МОЙ', 'ТВОЙ', 'ЕГО', 'ЕЁ']
    for token in sentence:
        group = []
        if token['upos'] in ['ADP', 'ADV'] and token['xpos'] != 'PR':
            #Нашли предлог, союз, теперь надо найти детей
            children = get_children_token(token, sentence)
            group.append(token)

            #получили детей. теперь от каждого ребенка-существительного идем пока он не станет токеном идем пока он
            for child in children:
                if child['upos'] in ['NOUN','VERB'] or child['xpos'] in mest or '_' in child['xpos']:
                    id = child['id']
                    head_id = child['head']
                    group = []
                    if head_id == token['id']:
                        group = [child, token]
                        saved_size = 1
                        if group not in groups:
                            groups.append(group)
                    else:
                        while token != sentence[id -1 ] and (sentence[id-1] == child or ((sentence[id - 1]['upos'] in ['ADP','ADV'] or sentence[id - 1]['xpos'] == 'PR') and (sentence[id - 1]['deprel'] in ['обст', 'сравнит', 'сравн-союзн', 'предл', 'количест'] or 'компл' in str(sentence[id - 1]['deprel'])))):
                            if sentence[id-1] not in group:
                                group.append(sentence[id-1])
                            id = sentence[id-1]['head']

                        if len(group) > 1 and sentence[id-1]==token and group not in groups:
                            if group not in groups:
                                groups.append(group)

    if len(groups) > 0:
        for group in groups:
            group_id = []
            for token in group:
                group_id.append(token['id'])

            ordered_id = sorted(group_id)
            text = ''

            for i in range(len(ordered_id)):
                text = text + sentence[ordered_id[i] - 1]['form'] + ' '
            max_id = -1

            for i in range(len(ordered_id)):
                if sentence[ordered_id[i] - 1]['head'] not in ordered_id:
                    max_id = ordered_id[i]
            token = sentence[max_id-1]

            new_token = create_sg(len(sentence) + 1, text, 'Г9', sentence[max_id-1]['head'], sentence[max_id-1]['deprel'])
            sentence.append(new_token)
            bool_new_group = True
            token['deprel'] = '_'
            token['head'] = len(sentence)

            for reb_token in group:
                if reb_token == sentence[max_id-1]:
                    reb_token['deprel'] = '_'
                cur_children_token = get_one_step_children_token(reb_token, sentence)
                for t in cur_children_token:
                    if t not in group:
                        t['head'] = len(sentence)

            #for elem in group:
            #    children = get_one_step_children_token(elem,sentence)
            #    for child in children:
            #        if child not in group and child['deprel']!='_':
            #            rebind_tokens(new_token_group,child)

        return bool_new_group

    return bool_new_group

