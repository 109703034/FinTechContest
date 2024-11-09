import spacy

def preprocess(text):
    nlp = spacy.load("zh_core_web_trf")  # 中文模型
    doc = nlp(text)

    # 抽取命名實體
    entities = [ent.text for ent in doc.ents]
    # for token in doc:
    #     print(token.text, token.pos_)
    selected_words = [token.text for token in doc if token.pos_ not in ("ADP", "PART", "PROPN") and token.text not in ["多少","是","為"]]
    new_sentence = "".join(selected_words)
    # print(new_sentence)
    return new_sentence

