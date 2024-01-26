"""Module that specifies data structures, namely Snippet and Snippets."""
import pickle
import random
from typing import Dict, List
from urllib.request import urlopen


class Snippet:
    def __init__(
        self, snippet_id: int, lines: List[str], url: str, author: str, language: str
    ) -> None:
        """Data for a single code snippet.

        Parameters
        ----------
        snippet_id : int
            Unique ID for each code snippet.
        lines : list[str]
            Text lines in the code snippet.
        url : str
            A link to the source of the code snippet (ie full url to github
            source file with lines permalinked)
        author : str
            The author of the code snippet (ie pallets/flask).
        language : str
            The programming language in which the code snippet is written.
        """
        self.snippet_id = snippet_id
        self.lines = lines
        self.url = url
        self.author = author
        self.language = language

    @classmethod
    def from_url(cls, snippet_id: int, url: str, language: str):
        """Create Snippet object from github permalink.

        A url must be of form:
        https://github.com/<USERNAME>/<REPO>/blob/<COMMIT_HASH>/path/to/file.ext#L<START>-L<END>

        For example:
        https://github.com/jaymody/linkipedia/blob/09f3ca27e1ad858a6a010d2ef3d0768cbb9dda36/src/main/java/com/linkipedia/Graph.java#L9-L31

        This will extract the code from the given url and create a Snippet
        object from it. The code will be assigned to lines, the url to url, and
        the author to <USERNAME>/<REPO>.

        Parameters
        ----------
        snippet_id : int
            Unique ID for the code snippet.
        url : str
            Github permalink.

        Returns
        -------
        Snippet
            Snippet object created using github permalink.
        """
        # author
        author = url.split("/blob/")[0].split("github.com/")[-1]

        # get line numbers
        l1, l2 = [int(n[1:]) for n in url.split("#")[-1].split("-")]

        # get code snippet lines
        # TODO: make this more efficient
        raw_url = url.replace("/blob/", "/raw/", 1)
        with urlopen(raw_url) as response:
            text = response.read().decode("utf-8")
        lines = text.splitlines()
        lines = lines[l1 - 1 : l2]
        # TODO: maybes use config tabs to spaces?
        lines = [line.rstrip().replace("\t", " " * 4) for line in lines]

        # if first line contains whitespace, remove that much whitespace from
        # the rest of the lines
        ws = lambda x: len(x) - len(x.lstrip())
        fws = ws(lines[0])
        lines = [line[min(ws(line), fws) :] for line in lines]

        return cls(snippet_id, lines, url, author, language)


class Snippets:
    def __init__(self, snippets: List[Snippet]) -> None:
        """Stores database of code snippets.

        Parameters
        ----------
        snippets : list[Snippet]
            A list of Snippet objects.
        """
        self.snippets = snippets
        self.index = 0
        self.shuffle()

    def __len__(self) -> int:
        """Returns number of snippets."""
        return len(self.snippets)

    def __iter__(self):
        for s in self.snippets:
            yield s

    def shuffle(self) -> None:
        """Shuffle the list of snippets."""
        random.shuffle(self.snippets)

    def current_snippet(self) -> Snippet:
        """Get current entry"""
        return self.snippets[self.index]

    def next_snippet(self) -> Snippet:
        """Returns the next entry in the list of code snippets."""
        self.index += 1
        self.index = self.index % len(self)
        return self.snippets[self.index]

    def prev_snippet(self) -> Snippet:
        """Returns the previous entry in the list of code snippets."""
        self.index -= 1
        self.index = self.index % len(self)
        return self.snippets[self.index]

    @staticmethod
    def load(filename: str, languages: List[str], max_lines: int, max_cols: int):
        """Loads snippets from specified filename.

        Parameters
        ----------
        filename : str
            A direct path to the filename to load snippets from.

        languages : list[str]
            List of string of languages to load snippets of.

        Returns
        -------
        Snippets
            Returns Snippets object loaded from filename.
        """
        languages = set(languages)

        with open(filename, "rb") as fi:
            snippets = pickle.load(fi)

        snippets.snippets = [
            s
            for s in snippets.snippets
            if s.language in languages
            and len(s.lines) <= max_lines
            and max(map(len, s.lines)) <= max_cols
        ]
        snippets.shuffle()
        return snippets

    def save(self, filename: str):
        """Saves current statistics to the specified pickle file.

        Parameters
        ----------
        filename : str
            File path to save stats to.
        """
        with open(filename, "wb") as fo:
            pickle.dump(self, fo)

    @classmethod
    def from_lang_to_urls_dict(cls, lang_to_urls_dict: Dict[str, List[str]]):
        """Creates snippets object from github permalinks.

        See Snippet.from_url() for more information.

        Parameters
        ----------
        urls : dict[str, list[str]]
            Dictionary of language (key) to list (value) of github permalinks.

        Returns
        -------
        Snippets
            Snippets object with snippets from urls.
        """
        # TODO: add try except if something goes wrong for a given url
        snippets = []
        for language, urls in lang_to_urls_dict.items():
            for i, url in enumerate(urls):
                try:
                    snippet = Snippet.from_url(i, url, language)
                    snippets.append(snippet)
                except:
                    print("Error downloading", url, "- SKIPPED")
        return cls(snippets)
