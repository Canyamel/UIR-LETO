from proc.proc_conllu import *

def rule_a_8(sentence: TokenList) -> bool:
    bool_new_group = False

    for token in sentence:
        if token['form'] == 'бы' and token['deprel'] == "аналит":
            children_token = [token]
            head_token = get_head(token, sentence)
            children_token.append(head_token)
            a8_children = []

            #if head_token['form'] == '_':
            #    break
            form = str(head_token['form']) + " " + str(token['form'])
            form = form.replace('.', '')
            form = form.replace(',', '')
            form = form.replace('-', '')

            a8_children += get_one_step_children_token(token, sentence)
            a8_children += get_one_step_children_token(head_token, sentence)

            new_token = create_sg(len(sentence) + 1, form, 'А8', head_token['head'], head_token['deprel'])
            sentence.append(new_token)

            for t in children_token:
                t['deprel'] = "_"
                t['head'] = len(sentence)

            for t in a8_children:
                t['head'] = len(sentence)

            bool_new_group = True

    return bool_new_group
