class transliterate:
    try:
        # Make english dictionary with pronounciation
        import cmudict
        english_dict = cmudict.dict()
    except ModuleNotFoundError:
        print("Need cmu dictionary with pronounciation. TRY 'pip install cmudict'")
        raise ModuleNotFoundError

    def __init__(self, arpa_kata_csv_file_path):
        # Arpabet syllable pronounciation to katakana dictionary
        import pandas as pd

        arpa_kata_df = pd.read_csv(arpa_kata_csv_file_path)
        self.arpa_kata_dict = {}
        for ak in arpa_kata_df.values:
            c1 = ak[0].replace("'", '').strip()
            v1 = ak[1].strip().split(':')
            self.arpa_kata_dict[c1] = v1
            if not c1[-1].isnumeric(): continue
            for st in ['0', '1', '2']:
                if c1[:-1] + st in self.arpa_kata_dict: continue
                self.arpa_kata_dict[c1[:-1] + st] = v1

    # Word break algorithm based on english dictionary
    @staticmethod
    def breakings(w):
        def wordbreak(s, i):
            if not s[i:]: return []
            p = ''
            a = []
            for c in s[i:-1]:
                p += c
                i += 1
                if not transliterate.english_dict.get(p) or len(transliterate.english_dict.get(p)) == 0: continue
                a += [[p] + arr for arr in wordbreak(s, i) if arr]
            p += s[-1]
            if not transliterate.english_dict.get(p) or len(transliterate.english_dict.get(p)) == 0: return a
            a += [[p]]
            return a
        a = wordbreak(w, 0)
        return a

    # Forms a single string based on [1, [2, 3], [5]] => [125, 135]
    @staticmethod
    def merger(l):
        if not l: return []
        if all([type(ll) is not list for ll in l]):
            return l
        if len(l) == 1: return transliterate.merger(l[0])
        b = transliterate.merger(l[0:int(len(l)/2)])
        c = transliterate.merger(l[int(len(l)/2):])
        if not c: return b
        if not b: return c
        return [w1 + w2 for w1 in b for w2 in c]

    def con_pronounciation_katakana(self, arpa_list):
        b_1 = []
        for c_b_i in range(len(arpa_list)):
            c_b = arpa_list[c_b_i]
            b_2 = []
            ps = transliterate.english_dict.get(c_b)
            for p in ps:
                i = 0
                k_w = []
                while i<len(p):
                    arpa_key = p[i]
                    if p[i][-1].isnumeric():
                        i += 1
                    elif i+1<len(p) and str(p[i+1][-1]).isnumeric():
                        arpa_key +=  ' ' + p[i+1]
                        i += 2
                    elif c_b_i != len(arpa_list)-1 and 'ッ' != self.arpa_kata_dict[p[i]][0] and i == len(p)-1:
                        k_w.append(['ッ'])
                        i += 1
                    else:
                        i += 1
                    k_w.append(self.arpa_kata_dict[arpa_key])
                b_2 += transliterate.merger(k_w)
            b_1.append(b_2)
        return b_1

    def english_to_katakana(self, english_words):
        english_kata_dict = {}
        ii = 0
        for w in english_words:
            english_kata_dict[w] = set()
            ii += 1
            if ii % 50 == 0: print(ii)
            w_splits = [[w]]  if transliterate.english_dict.get(w) and len(transliterate.english_dict.get(w)) != 0 else transliterate.breakings(w)
            max_split = 0
            max_split_arr = []
            for f in w_splits:
                ff = [w for w in f if len(w) > 2]
                if len(''.join(ff)) > max_split:
                    max_split = len(''.join(ff))
                    max_split_arr = [ff]
                elif len(''.join(ff)) == max_split:
                    max_split_arr.append(f)
            for b in max_split_arr:
                b_1 = self.con_pronounciation_katakana(b)
                english_kata_dict[w] = english_kata_dict[w].union(transliterate.merger(b_1))
        return english_kata_dict

if __name__ == '__main__':
    import sys
    list_to_translit = sys.argv[1:]
    t = transliterate('arpabet_katakana.csv')
    print(t.english_to_katakana(list_to_translit))
