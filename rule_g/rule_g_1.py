from proc.proc_conllu import *
import json

def rule_g_1(sentence: TokenList) -> bool:
    for head_token in sentence:
        bool_new_group = False
        if (head_token['xpos'] != 'Г1' or sentence[head_token['head'] - 1]['xpos'] != 'Г1' and head_token['deprel'] == '_') and head_token['id'] != 1:

            lemma = head_token['lemma']
            if lemma == '_':
                group_component_sg = get_group_component_sg(head_token, sentence)
                if len(group_component_sg) == 2:
                    for token in group_component_sg:
                        if token['head'] == head_token['id'] and token['deprel'] == '_' and token['upos'] != 'ADP':
                            lemma = token['lemma']
                            break
                else:
                    root_component = get_root_component_sg(head_token, sentence)
                    if root_component != None:
                        lemma = get_root_component_sg(head_token, sentence)['lemma']
                    else:
                        continue

            group_child_token = get_one_step_children_token(head_token, sentence)
            if len(group_child_token) > 0:
                with open("glossary/gl_rule_g_1.json", "r", encoding="utf-8") as json_file:
                    wordbook = json.load(json_file)
                for word in wordbook['words']:
                    if word['lemma'] == lemma.lower():
                        for child_token in group_child_token:
                            for magn in word['magn']:
                                if magn == child_token['lemma'].lower():
                                    bool_new_group = True
                                    break

            if bool_new_group:
                group_token = [head_token]
                for token in get_one_step_children_token(head_token, sentence):
                    group_token.extend(get_token_for_group(token, sentence))

                buf_group_token = group_token.copy()
                for token in buf_group_token:
                    if token['lemma'] == '_':
                        group_token.remove(token)
                        group_token.extend(get_group_component_sg(token, sentence))
                group_token.sort(key=lambda token: token['id'])
                phrase = ''
                for token in group_token:
                    phrase += token['form'] + ' '
                phrase = phrase[:-1]
                group_token = buf_group_token.copy()

                list_one_step_children_token = []
                for token in group_token:
                    list_one_step_children_token.extend(get_one_step_children_token(token, sentence))

                # Добавить новую группу и изменить связи между элементами ССГ
                for token in list_one_step_children_token:
                    if token not in group_token:
                        token['head'] = len(sentence) + 1
                sentence.append(create_sg(len(sentence) + 1, phrase, 'Г1', head_token['head'], head_token['deprel']))
                head_token['deprel'] = '_'
                head_token['head'] = len(sentence)

    return bool_new_group