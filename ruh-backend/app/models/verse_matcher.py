class VerseMatcher:
    def __init__(self, verses):
        self.verses = verses

    def match_verse(self, query):
        matched_verses = []
        for verse in self.verses:
            if self._is_match(verse, query):
                matched_verses.append(verse)
        return matched_verses

    def _is_match(self, verse, query):
        # Implement matching logic here
        return query.lower() in verse.lower()