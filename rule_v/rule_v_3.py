from proc.proc_conllu import *

def rule_v_3(sentence: TokenList) -> bool:
    bool_new_group = False
    for token in sentence:
        if (token['deprel'] == "подч-союзн" or token['deprel'] == "инф-союзн") and token['xpos'] not in ['В3']:
            child_tokens = get_children_token(token, sentence)
            group_token = [token]
            for child in child_tokens:
                group_token.append(child)

            if len(group_token) > 1:
                bool_new_group = True
                phrase = ""
                buf_group_token = group_token.copy()
                for t in group_token:
                    if t['lemma'] == '_':
                        buf_group_token.remove(t)
                        components_sg = get_group_all_component_sg(t, sentence)
                        for cmp in components_sg:
                            if cmp not in buf_group_token:
                                buf_group_token.append(cmp)

                buf_group_token.sort(key=lambda token: token['id'])
                for t in buf_group_token:
                    phrase += t['form'] + ' '
                phrase = phrase[:-1]

                sentence.append(create_sg(len(sentence) + 1, phrase, 'В3', sentence[token['head'] - 1]['head'], '_'))
                token['deprel'] = '_'
                token['head'] = len(sentence)

                for reb_token in group_token:
                    cur_children_token = get_one_step_children_token(reb_token, sentence)
                    for t in cur_children_token:
                        if t not in group_token:
                            t['head'] = len(sentence)

    return bool_new_group