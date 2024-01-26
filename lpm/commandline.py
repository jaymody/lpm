"""Module that specifies the lpm command-line interface.

Use `lpm -h` for help.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from . import __version__
from .game import Game
from .snippets import Snippets
from .stats import Stat, Stats

data_dir = Path.home().joinpath(".cache/lpm/")
os.makedirs(data_dir, exist_ok=True)
STATS_PATH = data_dir.joinpath("stats.pickle")
SNIPPETS_PATH = data_dir.joinpath("snippets.pickle")
CONFIG = {
    "max_lines": 40,
    "max_cols": 80,
    "colors": {
        "text": (15, 0),
        "correct": (46, 0),
        "incorrect": (196, 0),
        "quote": (250, 0),
        "status": (21, 0),
        "top_bar": (238, 0),
        "author": (51, 0),
        "prompt": (201, 0),
        "background": (0, 0),
    },
    "lang_to_urls": {
        "python": [
            r"https://github.com/jaymody/seq2seq_polynomial/blob/b3fc25121a1210b98a2fa6efec33af539812cad4/data.py#L76-L80",
            r"https://github.com/jaymody/seq2seq_polynomial/blob/b3fc25121a1210b98a2fa6efec33af539812cad4/tests.py#L4-L14",
            r"https://github.com/cslarsen/wpm/blob/6e48d8b750c7828166b67a532ff03d62584fb953/wpm/histogram.py#L44-L58",
            r"https://github.com/JessicaLim8/BrAsthma/blob/0d00169ee73be77a056dae1dd00e8699d31cb028/dp3.py#L32-L41",
            r"https://github.com/JessicaLim8/BrAsthma/blob/0d00169ee73be77a056dae1dd00e8699d31cb028/practice_mock.py#L1-L11",
            r"https://github.com/parappally/bball_api/blob/fefcc963b38a1d7ba613ee61a1c902cdaa8307d2/app.py#L52-L60",
            r"https://github.com/parappally/Guidin-George/blob/85a017baaaf619696a9898a8101fc3fdec4ce4a7/enghacks/geodistance.py#L3-L10",
            r"https://github.com/SamYu/stylist.ai/blob/d7ab3579d45c79385a6e0a0a2a15b52848090ae1/outfitpicker/outfit_dataset_manual_generator.py#L25-L31",
            r"https://github.com/jaymody/bert/blob/a9a3195c248432694fde4133068c75e67ee3756e/optimization.py#L159-L167",
            r"https://github.com/jaymody/bert/blob/a9a3195c248432694fde4133068c75e67ee3756e/run_classifier.py#L197-L204",
            r"https://github.com/jaymody/leetcode/blob/20ca7d6148a9ce66a91d6c147f34097bd681ad4d/python/867%20-%20Transpose%20Matrix.py#L11-L17",
        ],
        "javascript": [
            r"https://github.com/jaymody/jaymody.github.io/blob/84598e192475bb2be161994cd1543a83b0737acf/src/components/Deck.js#L1-L18",
            r"https://github.com/MaanavD/TLDR-Bot/blob/cd026ba24cb3f329bbedb135a9a8c168409b7cea/stdlib/MaanavD/slack-app/functions/commands/tldr.js#L24-L33",
            r"https://github.com/MaanavD/TLDR-Bot/blob/cd026ba24cb3f329bbedb135a9a8c168409b7cea/stdlib/MaanavD/slack-app/functions/commands/tldr.js#L77-L87",
            r"https://github.com/MaanavD/TLDR-Bot/blob/cd026ba24cb3f329bbedb135a9a8c168409b7cea/stdlib/MaanavD/slack-app/utils/format_message.js#L37-L48",
            r"https://github.com/MaanavD/SN8KRS/blob/a77b45e7539e5ee00875b2e7f20969a46410e958/models/shoe.model.js#L5-L15",
            r"https://github.com/MaanavD/SN8KRS/blob/a77b45e7539e5ee00875b2e7f20969a46410e958/routes/offers.js#L4-L11",
            r"https://github.com/MaanavD/SN8KRS/blob/a77b45e7539e5ee00875b2e7f20969a46410e958/client/src/App.js#L14-L23",
            r"https://github.com/MaanavD/SN8KRS/blob/a77b45e7539e5ee00875b2e7f20969a46410e958/client/src/index.js#L9-L14",
            r"https://github.com/JessicaLim8/VoicePrep/blob/975092f57365009bc3d4d2c2b78e1a2bd0b2bcca/client/src/pages/Results.js#L26-L34",
            r"https://github.com/JessicaLim8/VoicePrep/blob/975092f57365009bc3d4d2c2b78e1a2bd0b2bcca/client/src/pages/wordcounter.js#L1-L14",
        ],
        "java": [
            r"https://github.com/jaymody/Brawler64/blob/632b98b61e9ceeb16742926b57cc4a98a364abd3/src/game/KeyInput.java#L1-L18",
            r"https://github.com/MaanavD/Employmint/blob/f77551a2225c67891cc48c1d8014865d3d05d4b4/app/src/main/java/thacks/employmint/jobsearch.java#L79-L87",
            r"https://github.com/JessicaLim8/Linkipedia/blob/8880a1b8e6b08add67cdc4ad827c98d9bf7871f5/src/main/java/com/linkipedia/Node.java#L11-L23",
            r"https://github.com/JessicaLim8/ThinkTacToe/blob/c54e6a023fcc0c5357d444236b5dcf580b246135/src/thinktactoeGame/GameBoard.java#L10-L19",
            r"https://github.com/JessicaLim8/ThinkTacToe/blob/c54e6a023fcc0c5357d444236b5dcf580b246135/src/mathGame/MathGameState.java#L61-L71",
            r"https://github.com/jaymody/linkipedia/blob/09f3ca27e1ad858a6a010d2ef3d0768cbb9dda36/src/main/java/com/linkipedia/Sort.java#L69-L82",
            r"https://github.com/JessicaLim8/Linkipedia/blob/8880a1b8e6b08add67cdc4ad827c98d9bf7871f5/src/main/java/com/linkipedia/Search.java#L29-L37",
            r"https://github.com/jaymody/Brawler64/blob/632b98b61e9ceeb16742926b57cc4a98a364abd3/src/main/Main.java#L76-L82",
            r"https://github.com/jaymody/leetcode/blob/20ca7d6148a9ce66a91d6c147f34097bd681ad4d/java/509%20-%20Fibonacci%20Number.java#L10-L22",
            r"https://github.com/jaymody/leetcode/blob/20ca7d6148a9ce66a91d6c147f34097bd681ad4d/java/62%20-%20Unique%20Paths.java#L13-L25",
        ],
    },
}


def stats() -> None:
    """Display lifetime statistics and most recent game statistics."""
    from datetime import datetime, timedelta

    # TODO: make this better
    # TODO: only show last N things
    if not os.path.exists(STATS_PATH):
        print("No stats recorded")
        return

    statistics = Stats.load(STATS_PATH)

    lifetime = Stat()
    elapsed = 0
    i = len(statistics)
    print("last 5 games")
    print("------------")
    for s in statistics:
        lifetime.num_chars += s.num_chars
        lifetime.num_lines += s.num_lines
        lifetime.num_correct += s.num_correct
        lifetime.num_wrong += s.num_wrong
        elapsed += s.elapsed
        if i <= 5:
            print(s.end_time.strftime("%Y-%m-%d %H:%M:%S"), "  ", s)
        i -= 1

    lifetime.start_time = datetime.today()
    lifetime.end_time = lifetime.start_time + timedelta(0, elapsed)
    print("")
    print("lifetime stats")
    print("--------------")
    print(
        f"{len(statistics)} games | {lifetime.elapsed:.2f}s total elapsed | "
        f"{lifetime.lpm:.2f} avg lpm | {lifetime.wpm:.2f} avg wpm | "
        f"{lifetime.cpm:.2f} avg cpm | {lifetime.acc*100:.2f}% avg acc"
    )


def version() -> None:
    """Display the program version."""
    print(__version__)


def start(languages: List[str] = None):
    """Starts the lpm typing interface.

    Parameters
    ----------
    languages : list[str]
        Whitelist of programming languages to load code snippets for.
    """
    if not languages:
        languages = CONFIG["lang_to_urls"]["python"]

    for lang in languages:
        if lang.lower() not in CONFIG["lang_to_urls"]:
            print(
                "ERROR: one or more args are not valid languages, must be one of:\n",
                ", ".join(CONFIG["lang_to_urls"]),
            )
            return

    # load snippets
    if not os.path.exists(SNIPPETS_PATH):
        print("... downloading snippets ...")
        snippets = Snippets.from_lang_to_urls_dict(CONFIG["lang_to_urls"])
        snippets.save(SNIPPETS_PATH)
    snippets = Snippets.load(
        SNIPPETS_PATH,
        languages=languages,
        max_lines=CONFIG["max_lines"],
        max_cols=CONFIG["max_cols"],
    )
    if len(snippets) <= 0:
        print(
            "ERROR: no snippets were loaded, please modify (or reset) the "
            "settings to increase MAX_LINES and MAX_COLS"
        )
        sys.exit(1)

    # load stats
    if not os.path.exists(STATS_PATH):
        statistics = Stats([])
    else:
        statistics = Stats.load(STATS_PATH)

    with Game(
        snippets,
        statistics,
        CONFIG["max_lines"],
        CONFIG["max_cols"],
        CONFIG["colors"],
        STATS_PATH,
    ) as game:
        game.run()


def reset() -> None:
    """Interactive reset for settings, stats, and snippets."""

    stats_reset = input("Do you want to reset your lifetime statistics? (y/n): ")
    if stats_reset.lower() == "y":
        if os.path.exists(STATS_PATH):
            os.remove(STATS_PATH)
            print("User statistics were reset.\n")
        else:
            print("User statistics do not exist.\n")

    snippets_reset = input("Do you want to redownload snippets? (y/n): ")
    if snippets_reset.lower() == "y":
        print("... downloading snippets ...")
        snippets = Snippets.from_lang_to_urls_dict(CONFIG["lang_to_urls"])
        snippets.save(SNIPPETS_PATH)
        print("... done ...")


def cli() -> None:
    """Main entry point for lpm CLI."""
    if sys.version_info < (3, 6):
        print("lpm requires python >= 3.6")

    example_usages = [
        "lpm",
        "lpm python",
        "lpm java",
        "lpm python java",
        "lpm --help",
        "lpm --stats",
    ]
    parser = argparse.ArgumentParser(
        "lpm",
        description="Lines Per Minute, a typing tool made for programmers.",
        epilog="example usage:" + "\n  ".join([""] + example_usages),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "languages",
        type=str,
        default=CONFIG["lang_to_urls"],
        nargs="*",
        help="List of programming languages to filter code snippets. Must be "
        f"one of a {', '.join(CONFIG['lang_to_urls'])}. If no languages provided, "
        "all languages are loaded by default.",
    )
    parser.add_argument("-s", "--stats", action="store_true", help=stats.__doc__)
    parser.add_argument("-v", "--version", action="store_true", help=version.__doc__)
    parser.add_argument("--reset", action="store_true", help=reset.__doc__)

    args, unknown = parser.parse_known_args()
    if unknown:
        print("ERROR: invalid flag(s), please see lpm -h for more info")
    elif args.stats:
        stats()
    elif args.version:
        version()
    elif args.reset:
        reset()
    else:
        start(args.languages)
