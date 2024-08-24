from proc.proc_conllu import *

def get_good_children_new(token, children, sentence):
    mest = ['Я','МЫ','ТЫ','ВЫ','ОН','ОНО','ОНА','ОНИ',
            'МЕНЯ','НАС','ТЕБЯ','ВАС','ЕЕ','ЕЙ','ЕЁ','ИХ',
            'МНЕ','ТЕБЕ','ВАМ','ЕМУ','ЕЁ','ИМ',
            'МЕНЯ','НАС','ВАС','ЕГО',
            'НАМИ','ТОБОЙ','ВАМИ','ЕЮ','ИМИ', 'СЕЙ']
    max_group = []
    all_children = []
    for child in children:
        all_children.append(child)

    for child in children:
        if child['form'][0].isupper():
            id = int(child['id'] - 1)
            id_prev = -1

            while (((sentence[id]['upos'] in ['ADJ','ADV','NOUN'] or ('ДЕЕПР' in str(sentence[id]['feats']))) and (sentence[id]['form'][0].isupper() and id != 1)) or sentence[id]['lemma'] == 'ИМЯ' or sentence[id]['upos'] in ['CCONJ','PR']) and sentence[id]['deprel'] not in ['сочин','кратн', 'аппоз','кратно-длительн','вспом', 'квазиагент', 'соч-союзн', 'огранич'] and sentence[id]!=token and sentence[id]['lemma'] not in mest and id_prev != id:
                id_prev = sentence[id]['id']
                id = int(sentence[id]['head'] - 1)

            if sentence[id] == token:
                max_group.append(child)

    return max_group

def rule_g_18(sentence: TokenList) -> bool:
    bool_new_group = False
    groups = []
    for token in sentence:
        #поиск по существующим группам
        check = False
        for i in range(len(groups)):
            for j in range(len(groups[i])):
                if token == groups[i][j]:
                    check = True

        if token['upos'] == 'NOUN' and str(token['form'])[0].isupper() and check == False:
            all_children = get_children_token(token, sentence)
            we_got_in_the_end = get_good_children_new(token, all_children, sentence)

            if len(we_got_in_the_end) > 1:
                print('111')
                group_id = []
                we_got_in_the_end.append(token)
                children = get_one_step_children_token(token, sentence)
                '''
                for i in range(len(we_got_in_the_end)):
                    children = get_children(sentence[we_got_in_the_end[i]['id']-1],sentence)
                    #print(children)
                    group_id.append(we_got_in_the_end[i]['id'])
                prev = token
                for child in children:
                    if (child['upos'] in ['ADJ','ADV','NOUN'] or ('ДЕЕПР' in str(child['feats']))) and child not in we_got_in_the_end and child['deprel'] not in ['сочин', 'предик'] and child['lemma']not in ['ВЕСЬ']:
                        we_got_in_the_end.append(child)
                groups.append(we_got_in_the_end)
                #for token in sentence:
                #    if token['form'] == we_got_in_the_end[max_i]['form'] and token['head'] == we_got_in_the_end[max_i]['head']:
                #        rebind_tokens(new_token_group, token)
                '''
                groups.append(we_got_in_the_end)

    for group in groups:
        bool_new_group = True

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

        new_token = create_sg(len(sentence) + 1, text, 'Г18', sentence[max_id-1]['head'], sentence[max_id-1]['deprel'])
        sentence.append(new_token)

        token['head'] = len(sentence)
        token['deprel'] = '_'
        for elem in group:
            children = get_one_step_children_token(elem,sentence)
            for child in children:
                if child not in group:
                    child['head'] = len(sentence)

    return bool_new_group
