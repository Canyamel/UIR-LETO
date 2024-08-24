from proc.proc_conllu import *

def rule_a_1_2_3_4_9(sentence: TokenList) -> bool:
    bool_new_group = False
    array_a = ["_empty_"]

    rule = ['А1', 'А2', 'А3', 'А4', 'А9']
    for sub_categ in rule:

        if sub_categ == 'А1':
            array_a = ["тому назад", "в связи с", "во время", "по поводу", "в течение", "в качестве", "несмотря на",
                        "за счет", "со стороны", "В отличие от", "в виде", "по мере", "в соответствии с", "по сравнению с",
                        "вплоть до", "В ходе", "с помощью", "при помощи", "в отношении", "по отношению к", "в угоду",
                        "невзирая на", "в продолжение", "в заключение", "по причине", "в целях", "по сторонам", "в связи",
                        "в силу", "тем не менее", "прежде всего"]
        elif sub_categ == 'А2':
            array_a = ["и так далее,", "а то", "без того", "было б", "вряд ли", "всего навсего", "все же", "всё же",
                        "глядь и", "далеко не", "до чего", "добро бы", "если бы", "ещё бы", "и есть", "и так",
                        "как же", "как раз", "как так", "как то", "куда как", "ладно бы", "на что", "отнюдь не",
                        "просто напросто", "так уж", "туда же", "уж и", "хвать и", "что ж", "что ли", "лишь только"]
        elif sub_categ == 'А3':
            array_a = ["чтобы не", "как бы не", "как только", "лишь только", "в то время как", "после того как",
                        "потому что", "так как", "оттого что", "из-за того что", "вследствие того что", "для того чтобы",
                        "с тем чтобы", "сколько ни", "когда ни", "что ни", "что бы ни", "несмотря на то что",
                        "того что", "так что", "как будто"]
        elif sub_categ == 'А4':
            array_a = ["Не тот", "тот же", "тот же самый", "точно такой же"]
        elif sub_categ == 'А9':
            array_a = ["ни разу", "ни капельки", "ни один", "ни чуточки", "чувствовать себя", "вести себя"]

        category_a = sub_categ

        for token_phrase in array_a:
            i = 0
            while i + 1 < len(sentence):
                phrase = token_phrase.split()

                j = 0
                for word in phrase:
                    if str(sentence[i + j]['form']).lower().replace(",", "") == str(word).lower():
                        j += 1
                    elif j > 0:
                        j -= 1
                    if j == len(phrase):
                        break

                if j == len(phrase):
                    j = 0

                    min_level = get_level(sentence[i + j], sentence)
                    min_index = i + j
                    deprel = sentence[i + j]['deprel']
                    children = get_one_step_children_token(sentence[i + j], sentence)
                    sentence[i + j]['deprel'] = "_"
                    children.insert(0, sentence[i + j])
                    j += 1

                    while j < len(phrase):
                        if get_level(sentence[i + j], sentence) <= min_level:
                            min_level = get_level(sentence[i + j], sentence)
                            min_index = i + j
                            deprel = sentence[i + j]['deprel']
                        children += get_one_step_children_token(sentence[i + j], sentence)
                        sentence[i + j]['deprel'] = "_"
                        children.insert(0, sentence[i + j])
                        j += 1

                    new_token = create_sg(len(sentence) + 1, token_phrase, category_a, sentence[min_index]['head'], deprel)
                    sentence.append(new_token)

                    for token in children:
                        token['head'] = new_token['id']

                    i += 1
                    bool_new_group = True
                i += 1

    return bool_new_group
