from proc.proc_conllu import *

def rule_a_3_c3(sentence: TokenList) -> bool:
    bool_new_group = False
    array_a = ["как…так и"]

    for token_phrase in array_a:
        i = j = k = 0
        phrase_parts = token_phrase.split("…")
        phrase = phrase_parts[0].split()
        tokens_array_phrases_1 = []
        tokens_array_phrases_2 = []

        while i + len(phrase) < len(sentence):
            tokens_array_phrases_1 = []
            j = 0
            for word in phrase:
                if str(sentence[i + j]['lemma']).lower() == str(word).lower():
                    tokens_array_phrases_1.append(sentence[i + j])
                    j += 1
                if j == len(phrase):
                    break
            if j == len(phrase):
                break
            i += 1

        if j == len(phrase):
            phrase = phrase_parts[1].split()
            while i + j + len(phrase) < len(sentence):
                tokens_array_phrases_2 = []
                k = 0
                for word in phrase:
                    if str(sentence[i + j + k]['lemma']).lower() == str(word).lower():
                        tokens_array_phrases_2.append(sentence[i + j + k])
                        k += 1
                    if k == len(phrase):
                        break
                if k == len(phrase):
                    break
                i += 1

            if k == len(phrase):
                if tokens_array_phrases_1[0]['head'] == tokens_array_phrases_2[0]['head'] and \
                        not sentence.filter(head=tokens_array_phrases_2[0]['id']):

                    children_token = tokens_array_phrases_1 + tokens_array_phrases_2

                    head_token = get_head(tokens_array_phrases_1[0], sentence)
                    children_token += get_one_step_children_token(tokens_array_phrases_1[0], sentence)
                    children_token.append(head_token)

                    new_token = create_sg(len(sentence) + 1, token_phrase, 'А3', head_token['id'], 'сравнит')
                    sentence.append(new_token)

                    phrase = phrase_parts[0].split() + phrase_parts[1].split()

                    for token in children_token:
                        for word in phrase:
                            if str(token['lemma']).lower() == str(word).lower():
                                token['deprel'] = "_"
                                token['head'] = len(sentence)
                                cur_children_token = get_one_step_children_token(token, sentence)
                                for t in cur_children_token:
                                    t['head'] = len(sentence)

                    bool_new_group = True

    return bool_new_group
