from proc.proc_conllu import *

def rule_v_5(sentence: TokenList) -> bool:
    bool_new_group = True
    memory = []
    for t in sentence:
        if t['deprel'] == "соотнос" and t['xpos'] == 'PR' and t['misc'] != 'В5':
            head_token = get_head(t, sentence)
            memory.append(t['form'])
            siblings = get_one_step_children_token(head_token, sentence)
            right_sibling = 'sibling'
            right_child = 'child'

            for i in siblings:
                if i['deprel'] == 'предл' and i['upos'] == 'NOUN':
                    right_sibling = i
            children = get_one_step_children_token(t, sentence)

            for k in children:
                if k['deprel'] == 'предл' and k['upos'] == 'NOUN':
                    right_child = k

            if right_sibling == 'sibling':
                return 0

            if right_child == 'child':
                return 0

            t['misc'] = 'В5'
            siblings.remove(t)
            siblings.remove(right_sibling)
            children.remove(right_child)

            bool_new_group = True
            token_phrase_1 = head_token['form'] + " " + right_sibling['form']
            token_phrase_2 = t['form'] + " " + right_child['form']

            new_token = create_sg(len(sentence) + 1, token_phrase_2, 'В5', sentence[t['head'] - 1]['head'], '_')
            sentence.append(new_token)

            lower_children = get_one_step_children_token(right_child, sentence)

            for k in lower_children:
                k['head'] = len(sentence)

            for c in children:
                c['head'] = len(sentence)

            t['head'] = len(sentence)
            t['deprel'] = "_"
            #siblings.append(new_token)

            sentence.append(create_sg(len(sentence) + 1, token_phrase_1, 'В5', head_token['head'], head_token['deprel']))

            head_token['head'] = len(sentence)

            for s in siblings:
                s['head'] = len(sentence)

            upper_children = get_one_step_children_token(right_sibling, sentence)
            for f in upper_children:
                f['head'] = len(sentence)

            head_token['deprel'] = "_"
    '''
    for t in group_tokens:
        if t['form'] in memory and t['deprel'] == '_':
            t['deprel'] = "соотнос"
    '''
    return bool_new_group