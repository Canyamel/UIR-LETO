from proc.proc_conllu import *
from glossary.gl_rule_g_17 import *

def rule_g_17(sentence):
    bool_new_group = False
    phraz = []
    groups = []
    #Наполнили массив леммами идиом
    filler_of_phraz(phraz)
    #print(len(phraz))
    for token in sentence:
        #проходим по всем элементам предложения, ищем совпадения с хотя бы одном словом из массива лемм.
        #находим начало, находим конец. требуется чтобы между элементами не было различных других слов не более чем одного
        for one_phraz in phraz:
            if token['lemma'] == one_phraz[-1]:
                #найдено первое вхождение.
                group = []
                i = token['id'] - 1
                while sentence[i]['lemma'] in one_phraz and i > 0:
                    group.insert (0, sentence[i])
                    i -= 1

                if len(group) == len(one_phraz) and len(group) > 1 and group not in groups:
                    groups.append(group)

    if len(groups) >= 0:
        bool_new_group = True
        for group in groups:
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

            sentence.append(create_sg(len(sentence) + 1, text, 'Г17', sentence[max_id-1]['head'], sentence[max_id-1]['deprel']))
            token['head'] = len(sentence)
            token['deprel'] = '_'

    return bool_new_group