import regex

# import tiktoken


class Trie:
    """Useful for determing allowed tokens when trying to guide
    a model. A faster way to find all tokens that match a regex,
    or are candidates for a completion.

    Example, if the target is Hello, then tokens [H, He, Hell, Hello]
    should all be valid generations. The candidates function here is slowwww
    since it scans over all trie keys (due to regex allowing complicated patterns
    we have to check each case by case.).
    """

    def __init__(self):
        self._d = {}

    def add(self, token: str, index: int):
        d = self._d
        for x in token:
            if x not in d:
                d[x] = {}
            d = d[x]
        d[None] = index
        return self

    def get(self, token: str) -> int:
        d = self._d
        for x in token:
            if x not in d:
                return -1
            d = d[x]
        return d.get(None, -1)

    def delete(self, token: str, d=None):
        d = self._d
        ds = []
        for x in token:
            if x in d:
                ds.append(d)
            else:
                return False
            d = d[x]
        if True not in d:
            return False
        d.pop(None)
        for d, x in zip(reversed(ds), reversed(token)):
            if d.get(x):
                break
            d.pop(x)
        return True

    def regex_candidates(self, pattern: str, prefix: str = "") -> list[dict[str, int]]:
        """This is useful when you want to match a response-level regex, but need candidates
        for the next token.
        For example, if pattern='[a-z]+[0-9]+[a-z]+, and we have generated abc123d
        Then we can pass prefix='abc123d' and we will only get [a-z] as allowed generations.
        """
        res: list[dict[str, int]] = []
        q = [(self._d, "")]
        while q:
            d, s = q.pop()
            if None in d and s:
                res.append(dict(token=s, index=d[None]))
            for k, v in d.items():
                if k is not None:
                    cur = s + k
                    if regex.fullmatch(pattern, prefix + cur, partial=True):
                        q.append((v, cur))
        return res

    def candidates(self, pattern: str) -> list[dict[str, int]]:
        d = self._d
        res: list[dict[str, int]] = []
        for i, x in enumerate(pattern):
            if i and None in d:
                res.append({"index": d[None], "token": pattern[:i]})
            if x not in d:
                return res
            d = d[x]
        if None in d:
            res.append({"index": d[None], "token": pattern})
        return res

    # def _token_path(self, pattern: str):
    #     """This is never needed. Since the tokenizer can tokenize anything,
    #     there will never be a case where taking one early tokenization choice prevents
    #     tokenizing the full pattern. This is slow and has exponential blowup.

    #     Suppose you want to generate Washington D.C. you might get back a list of
    #     first choices for tokens as:
    #     [{'index': 258, 'token': ''},
    #     {'index': 31822, 'token': ' '},
    #     {'index': 348, 'token': ' W'},
    #     {'index': 12404, 'token': ' Wa'},
    #     {'index': 7261, 'token': ' Was'},
    #     {'index': 2872, 'token': ' Wash'},
    #     {'index': 3004, 'token': ' Washington'}]

    #     This opens up a tree of potential paths forward in order to ultimately generate
    #     our target. We could start at ' Wa', or as ' Was', each of which has different future
    #     tokens available to it. To construct the tree, we take each possible path, and only add it
    #     if it terminates in the desired pattern.
    #     """
    #     res: list[list[str]] = []
    #     candidates = self.candidates(pattern=pattern)
    #     if not candidates:
    #         return res
    #     for k in candidates:
    #         k = k["token"]
    #         if k == pattern:
    #             res.append([k])
    #         else:
    #             if cur := self._token_path(pattern=pattern[len(k) :]):
    #                 for x in cur:
    #                     res.append([k] + x)
    #     return res

    # def logit_bias(
    #     self, pattern: str, bias: float, is_regex: bool = True, prefix: str = ""
    # ) -> dict[int, float]:
    #     if is_regex:
    #         arr = self.regex_candidates(pattern=pattern, prefix=prefix)
    #     else:
    #         arr = self.candidates(pattern=pattern)
    #     return {x["index"]: bias for x in arr}
