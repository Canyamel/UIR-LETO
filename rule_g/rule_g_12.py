from proc.proc_conllu import *

def rule_g_12(sentence: TokenList) -> bool:
    bool_new_group = False
    quant = [
        "МНОГО", "МАЛО", "НЕМНОГО", "НЕМАЛО",
        "НЕСКОЛЬКО", "МНОГИЕ", "НЕМНОГИЕ", "БОЛЬШИНСТВО",
        "МЕНЬШИНСТВО", "МНОГОЕ","НЕМНОГОЕ"
    ]
    word_number_list = ['ОДИН', 'ДВА', 'ТРИ', 'ЧЕТЫРЕ', 'ПЯТЬ', 'ШЕСТЬ', 'СЕМЬ', 'ВОСЕМЬ', 'ДЕВЯТЬ',
                'ДЕСЯТЬ', 'ОДИННАДЦАТЬ', 'ДВЕНАДЦАТЬ', 'ТРИНАДЦАТЬ', 'ЧЕТЫРНАДЦАТЬ', 'ПЯТНАДЦАТЬ', 'ШЕСТНАДЦАТЬ', 'СЕМНАДЦАТЬ',
                'ВОСЕМНАДЦАТЬ', 'ДЕВЯТЬНАДЦАТЬ',
                'ДВАДЦАТЬ', 'ТРИДЦАТЬ', 'СОРОК', 'ПЯТЬДЕСЯТ', 'ШЕСТЬДЕСЯТ', 'СЕМЬДЕСЯТ', 'ВОСЕМДЕСЯТ', 'ДЕВЯНОСТО',
                'СТО', 'ДВЕСТИ', 'ТРИСТА', 'ЧЕТЫРЕСТА', 'ПЯТЬСОТ', 'ШЕСТЬСОТ', 'СЕМЬСОТ', 'ВОСЕМЬСОТ', 'ДЕВЯТЬСОТ', 'ТЫСЯЧА',
                'МИЛЛИОН', 'МИЛЛИАРД', 'ТРИЛЛИОН',
                'ПЕРВЫЙ', 'ВТОРОЙ', 'ТРЕТИЙ', 'ЧЕТВЕРТЫЙ', 'ПЯТЫЙ', 'ШЕСТОЙ', 'СЕДЬМОЙ', 'ВОСЬМОЙ', 'ДЕВЯТЫЙ', 'ДЕСЯТЫЙ',
                'ОДИННАДЦАТЫЙ', 'ДВЕНАДЦАТЫЙ', 'ТРИНАДЦАТЫЙ', 'ЧЕТЫРНАДЦАТЫЙ', 'ПЯТНАДЦАТЫЙ', 'ШЕСТНАДЦАТЫЙ', 'СЕМНАДЦАТЫЙ',
                'ВОСЕМНАДЦАТЫЙ', 'ДЕВЯТЬНАДЦАТЫЙ',
                'ДВАДЦАТЫЙ', 'ТРИДЦАТЫЙ', 'СОРОКОВОЙ', 'ПЯТИДЕСЯТЫЙ', 'ШЕСТИДЕСЯТЫЙ', 'СЕМИДЕСЯТЫЙ', 'ВОСМИДЕСЯТЫЙ', 'ДЕВЯНОСТЫЙ',
                'СОТЫЙ', 'ДВУХСОТЫЙ', 'ТРЕХСОТЫЙ', 'ЧЕТЫРЕХСОТЫЙ', 'ПЯТИСОТЫЙ', 'ШЕСТИСОТЫЙ', 'СЕМИСОТ', 'ВОСЬМИСОТЫЙ', 'ДЕВЯТИСОТЫЙ',
                'ТЫСЯЧНЫЙ', 'МИЛЛИОННЫЙ', 'МИЛЛИАРДНЫЙ']
    groups = []

    for token in sentence:
        if token['xpos'] == 'b3' or token['upos'] == 'NUM':
            head = sentence[token['head']-1]
            children_of_num_b3 = get_one_step_children_token(token, sentence)
            t = None
            fl = False
            for c in children_of_num_b3:
                if c['upos']== 'NOUN' and c['deprel'] == 'квазиагент' and c['form'] not in word_number_list:
                    t = c
                    fl = True
            if head['upos']== 'NOUN' and head['lemma'] not in word_number_list:
                good_children = []
                children = get_one_step_children_token(head, sentence)
                for child in children:
                    if child != token and child['deprel'] in ['опред', 'атриб', 'композ','аппоз']:
                        all_children = []
                        all_children = get_children_token(child, sentence)
                        all_children.append(child)
                        good_children = good_children + all_children
                if len(good_children) > 0:
                    good_children.append(head)
                    groups.append(good_children)

            elif fl:
                all_children = []
                all_children = get_children_token(t, sentence)
                all_children.append(t)
                if len(all_children) > 1:
                    groups.append(all_children)

        elif token['lemma'] in quant and token['upos']!='NOUN':
            head = sentence[token['head']-1]
            if token['deprel'] == 'опред':
                if head['upos']== 'NOUN':
                    good_children = []
                    children = get_one_step_children_token(head, sentence)
                    for child in children:
                        if child != token and child['deprel'] in ['опред', 'атриб', 'композ','аппоз']:
                            all_children = []
                            all_children = get_children_token(child, sentence)
                            all_children.append(child)
                            good_children.append(all_children)

                    if len(good_children) > 0:
                        groups = groups + good_children

            elif token['deprel'] not in ['обст', 'опред']:
                children = get_one_step_children_token(token,sentence)
                good_children = []

                for child in children:
                    if child['deprel'] == 'электив':
                        all_children = []
                        all_children = get_children_token(child, sentence)
                        all_children.append(child)
                        good_children.append(all_children)
                    elif child['upos'] == 'NOUN':
                        all_children = []
                        all_children = get_children_token(child, sentence)
                        all_children.append(child)
                        good_children.append(all_children)

                if len(good_children) > 0:
                    groups = groups + good_children

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

                sentence.append(create_sg(len(sentence) + 1, text, 'Г12', sentence[max_id-1]['head'], sentence[max_id-1]['deprel']))
                token['head'] = len(sentence)
                token['deprel'] = '_'

        return bool_new_group

    return bool_new_group