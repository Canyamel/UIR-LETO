from proc.proc_conllu import *

#Реализация подкритерия Б3
def rule_b_3(sentence: TokenList) -> bool:
    bool_new_group = False
    arr_of_sg_tokens = []
    count = 0
    flag = 0
    head_tokens_list = []
    text_group = ''
    num_str = '0123456789'
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

    for token in sentence:
        if token['form'] is None:
            continue

        if (token['lemma'] in word_number_list or token['form'][0] in num_str) and flag == 0:
            head_tokens_list.append(token)
            flag = 1

        if token['lemma'] not in word_number_list and token['form'][0] not in num_str:
            flag = 0

    for head_token in head_tokens_list:
        text_group = head_token['form'] + ' '
        arr_of_sg_tokens.append(head_token)
        count = 1
        flag = 1

        #Ищем подряд идущие группы, параллельно создавая "текст" возможной СГ
        for current_token in sentence[head_token['id']:]:
            if current_token['form'] is None:
                continue

            if head_token in get_one_step_children_token(current_token, sentence) and (current_token['lemma'] in word_number_list or current_token['form'][0] in num_str):
                head_token = current_token

            if (current_token['lemma'] in word_number_list or current_token['form'][0] in num_str) and flag:
                count += 1
                text_group += current_token['form'] + ' '
                arr_of_sg_tokens.append(current_token)

            if current_token['lemma'] not in word_number_list and current_token['form'][0] not in num_str:
                break

        if count > 1: #количество слов в названии токена > 1, значит возможно это составное числительное
            flag_coord = 1  # флаг, равный 1, если полученное выражение - составное числительное, и 0 - иначе.
            #проверка на наличие подчинительной связи, говорящая о том, что это не является составным числительным:
            arr_coord_tokens = []
            arr_coord_tokens = get_children_token(head_token, sentence)

            for worst_token in arr_coord_tokens:
                if worst_token['form'] is None:
                    continue

                if worst_token['id'] in get_all_id(arr_of_sg_tokens) and worst_token['deprel'] in ('сочин', 'кратн'):
                    flag_coord = 0
                    break

            #проверка на то, что у родителя вершины группы только один ребенок, входящий также в эту группу, иначе это не составное числительное:
            counter = 0
            for worst_token_2 in get_one_step_children_token(get_head(head_token, sentence), sentence):
                if worst_token_2['form'] is None:
                    continue

                if worst_token_2['id'] in get_all_id(arr_of_sg_tokens):
                    counter += 1

            if counter > 1:
                flag_coord = 0

            bool_not_a5 = False # Временный костыль, пока нет rule_a_5
            for t_a5 in arr_of_sg_tokens:
                if t_a5['head'] != head_token['id'] and t_a5 != head_token:
                    bool_not_a5 = True

            if bool_not_a5 == False:
                if flag_coord: #если флажок пережил проверки, значит имеем случай составных числительных.
                    new_token = create_sg(len(sentence) + 1, text_group, 'Б3', head_token['head'], head_token['deprel'])
                    sentence.append(new_token)
                    bool_new_group = True
                    head_token['deprel'] = '_'
                    head_token['head'] = len(sentence)

                    #Момент с перепривязкой нижележащих токенов
                    for reb_token in arr_of_sg_tokens:
                        cur_children_token = get_one_step_children_token(reb_token, sentence)
                        for t in cur_children_token:
                            if t not in arr_of_sg_tokens:
                                t['head'] = len(sentence)

        text_group = ''
        arr_of_sg_tokens = []

    return bool_new_group

