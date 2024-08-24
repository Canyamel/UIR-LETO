from proc.proc_conllu import *

def rule_a_3_c1(sentence: TokenList) -> bool:
    M = 0
    main_index_t = 0
    bool_new_group = False
    array_a = []

    while M < 1:
        if M == 0:
            main_index_t = 0
            array_a = ["ни…ни", "либо…либо", "или…или", "и…и", " то…то"]

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
                    phrase = phrase_parts[1].split()
                    z = i
                    while z + j + len(phrase) < len(sentence):
                        tokens_array_phrases_2 = []
                        k = 0
                        for word in phrase:
                            if str(sentence[z + j + k]['lemma']).lower() == str(word).lower():
                                tokens_array_phrases_2.append(sentence[z + j + k])
                                k += 1
                            if k == len(phrase):
                                break
                        if k == len(phrase):
                            break
                        z += 1

                    if k == len(phrase):
                        if (tokens_array_phrases_1[main_index_t]['id'] == tokens_array_phrases_2[main_index_t]['head']) \
                                or (
                                tokens_array_phrases_1[main_index_t]['head'] == tokens_array_phrases_2[main_index_t][
                            'id']):

                            children_token = tokens_array_phrases_1 + tokens_array_phrases_2

                            min_level = get_level(children_token[0], sentence)
                            token_min_index = children_token[0]

                            for token in children_token:
                                if min_level > get_level(token, sentence):
                                    min_level = get_level(token, sentence)
                                    token_min_index = token

                            children_token += get_one_step_children_token(token_min_index, sentence)

                            head_token = get_head(token_min_index, sentence)
                            children_token.append(head_token)

                            new_token = create_sg(len(sentence) + 1, token_phrase, 'А3', head_token['id'], 'сочин')
                            sentence.append(new_token)

                            for token in children_token:
                                for word in phrase:
                                    if str(token['lemma']).lower() == str(word).lower():
                                        token['deprel'] = "_"
                                        token['head'] = len(sentence)
                                        cur_children_token = get_one_step_children_token(token, sentence)
                                        for t in cur_children_token:
                                            t['head'] = len(sentence)

                            bool_new_group = True
                i += 1
        M += 1

    return bool_new_group
