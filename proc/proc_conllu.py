from conllu.models import TokenList, Token

def takeIdToken(token):
    return token['id']

# Возвращает группу зависимых токенов от данного токена (кроме тех, что входят в состав СГ)
def get_children_token(head_token: Token, group_tokens: TokenList) -> list:
    children_tokens = []
    for token in group_tokens:
        if token['head'] == head_token['id'] and token['deprel'] != '_':
            children_tokens.append(token)
            children_tokens.extend(get_children_token(token, group_tokens))
    return children_tokens

# Возвращает группу зависимых токенов от данного токена, что находятся на расстоянии равной единице (кроме тех, что входят в его состав, если такие есть)
def get_one_step_children_token(head_token: Token, sentence: TokenList) -> list:
    group_one_step_child_token = []
    for token in sentence:
        if token['id'] != 1 and token['head'] != 1 and token['id'] != head_token['id']:
            if token['head'] == head_token['id'] and token['deprel'] != '_':
                    group_one_step_child_token.append(token)
    return group_one_step_child_token

# Возвращает первый компонент СГ
def get_group_component_sg(head_token: Token, sentence: TokenList) -> list:
    components = []
    for token in sentence:
        if head_token['id'] == token['head'] and token['deprel'] == '_':
            if token['lemma'] != '_':
                components.append(token)
            else:
                components.extend(get_group_component_sg(token, sentence))
            components.extend(get_children_token(token, sentence))
    return components

def get_group_all_component_sg(head_token: Token, sentence: TokenList) -> list:
    components = []
    for token in sentence:
        if head_token['id'] == token['head'] and token['deprel'] == '_':
            if token['lemma'] == '_':
                components.extend(get_group_all_component_sg(token, sentence))
            else:
                components.append(token)
            for child_token in get_children_token(token, sentence):
                if child_token['lemma'] == '_':
                    components.extend(get_group_all_component_sg(child_token, sentence))
                else:
                    components.append(child_token)
    return components

def get_root_component_sg(head_token: Token, sentence: TokenList) -> list:
    for token in sentence:
        if head_token['id'] == token['head'] and token['deprel'] == '_':
            head_token = token
            if head_token['lemma'] == '_':
                head_token = get_root_component_sg(head_token, sentence)
            return head_token
    return None

def get_id_head_token(token: Token, sentence: TokenList) -> Token:
    if token['head'] == 1 or token['id'] == 1:
        return 0

    elif token['deprel'] != '_':
        if sentence[token['head'] - 1]['lemma'] != '_':
            return token['head']
        else:
            return get_root_component_sg(sentence[token['head'] - 1], sentence)['id']

    elif token['deprel'] == '_':
        return get_id_head_token(sentence[token['head'] - 1], sentence)

# Возвращает все пары отношений в предложении (элементы пары упорядочны по возрастнию)
def get_sorted_pairs(sentence: TokenList) -> list:
    pairs = []
    id_head_token = 0
    for token in sentence:
        if token['lemma'] != '_' and token['head'] != 0 and token['head'] != 1:
            if token['deprel'] != '_' and sentence[token['head'] - 1]['lemma'] != '_':
                id_head_token = token['head']
            elif token['deprel'] != '_' and sentence[token['head'] - 1]['lemma'] == '_':
                id_head_token = get_root_component_sg(sentence[token['head'] - 1], sentence)['id']
            else:
                if get_root_component_sg(sentence[token['head'] - 1], sentence)['id'] == token['id']:
                    id_head_token = get_id_head_token(token, sentence)
                else:
                    continue
            if id_head_token == 0:
                continue
            pair = [token['id'], id_head_token]
            pair.sort()
            pairs.append(pair)
    return pairs

# Проверяет наличие определённой морфологической характеристики у токена
def check_feat(token: Token, feat: str) -> bool:
    if token['feats'] != None:
        if feat in str(list(token['feats'].keys())[0]):
            return True
    return False

def get_head(token: Token, group_tokens: TokenList) -> Token:
    return group_tokens.filter(id=token['head'])[0]

def get_level(token: Token, group_tokens: TokenList) -> int:
    i = 0
    while 1:
        if token['head'] == '0' or token['head'] == 0:
            return i
        else:
            i += 1
        if i > 100:
            return 100
        token = get_head(token, group_tokens)

def get_all_id(arr_token):
    arr_id = []
    for token in arr_token:
        arr_id.append(token['id'])
    return arr_id

# Возвращает новый токен-СГ
def create_sg(id: int, upos: str, xpos: str, head: int, deprel: str) -> Token:
    return Token(
            id = id,
            form = '_',
            lemma = '_',
            upos = upos,
            xpos = xpos,
            feats = None,
            head = head,
            deprel = deprel,
            deps = None,
            misc = None
            )

def get_token_for_group(token: Token, sentence: TokenList):
    if token['deprel'] not in ['сент-соч', 'кратн', 'релят', 'разъяснит', 'примыкат', 'подч-союзн', 'инф-союзн', 'сравн-союзн', 'сравнит', 'эксплет']:
        group_child_token = [token]
        for child_token in get_one_step_children_token(token, sentence):
            group_child_token.extend(get_token_for_group(child_token, sentence))
        return group_child_token
    else:
        return []