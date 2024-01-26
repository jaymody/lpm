"""Module for tracking and computing lpm statistics."""
import pickle
from datetime import datetime

# TODO: save stats to a csv instead of pickle so it's more efficient


def lines_per_minute(num_lines: int, elapsed: float) -> float:
    """Calculates lines per minute.

    Parameters
    ----------
    num_lines : int
        Number of lines typed during elapsed time.
    elapsed : float
        Number of seconds elapsed in user's typing.

    Returnsj
    -------
    float
        Number of lines per minute a user is typing.
    """
    return 60 * num_lines / elapsed


def words_per_minute(num_chars: int, elapsed: float) -> float:
    """Calculates words per minute based on average 5.6 characters per word.

    Parameters
    ----------
    num_chars : int
        Number of characters typed during elapsed time.
    elapsed : float
        Number of seconds elapsed in user's typing.

    Returns
    -------
    float
        Number of words per minute a user is typing.
    """
    return 60 * (num_chars / 5.6) / elapsed


def characters_per_minute(num_chars: int, elapsed: float) -> float:
    """Calculates characters per minute.

    Parameters
    ----------
    num_chars : int
        Number of characters typed during elapsed time.
    elapsed : float
        Number of seconds elapsed in user's typing.

    Returns
    -------
    float
        Number of characters per minute a user is typing.
    """
    return 60 * num_chars / elapsed


def accuracy(correct: int, wrong: int) -> float:
    """Calculates user accuracy for a given section.

    Parameters
    ----------
    correct : int
        Number of characters correctly typed
    wrong : int
        Number of characters incorrectly typed

    Returns
    -------
    float
        The user's fractional accuracy for the given accuracy
    """
    return correct / (correct + wrong)


class Stat:
    TIME_STR_FMT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, start_time: datetime = None, end_time: datetime = None):
        """Statistics for a single snippet attempt.

        Parameters
        ----------
        start_time : datetime
            Datetime object for when attempt was started.
        end_time : datetime, optional
            Datetime object for when attempt was completed.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.num_lines = 0
        self.num_chars = 0
        self.num_correct = 0
        self.num_wrong = 0

    def start(self):
        """Set start_time to the current time (ie the code snippet attempt has started)."""
        self.start_time = datetime.now()

    def stop(self):
        """Set end_time to the current time (ie the code snippet attempt is done)."""
        self.end_time = datetime.now()

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds since stat was started."""
        if self.start_time is None:
            return 0
        if self.end_time is None:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    @property
    def lpm(self) -> float:
        """Lines per minute."""
        if self.start_time is None:
            return 0
        try:
            return lines_per_minute(self.num_lines, self.elapsed)
        except ZeroDivisionError:
            return 0

    @property
    def wpm(self) -> float:
        """Words per minute."""
        if self.start_time is None:
            return 0
        try:
            return words_per_minute(self.num_chars, self.elapsed)
        except ZeroDivisionError:
            return 0

    @property
    def cpm(self) -> float:
        """Characters per minute."""
        if self.start_time is None:
            return 0
        try:
            return characters_per_minute(self.num_chars, self.elapsed)
        except ZeroDivisionError:
            return 0

    @property
    def acc(self) -> float:
        """Accuracy."""
        if self.start_time is None:
            return 0
        if not self.num_correct + self.num_wrong > 0:
            return 0
        try:
            return accuracy(self.num_correct, self.num_wrong)
        except ZeroDivisionError:
            return 0

    def __eq__(self, other) -> bool:
        """Check two Stat objects are equal.

        Parameter
        ---------
        other : Stat
            Other Stat object to check equality of.

        Returns
        -------
        bool
            Whether self is equivalent to other.
        """
        return self.__dict__ == other.__dict__

    def __str__(self) -> str:
        return f"{self.elapsed:.2f}s  {self.lpm:.2f} lpm  {self.wpm:.2f} wpm  {self.cpm:.2f} cpm  {self.acc*100:.2f}% acc"


class Stats:
    def __init__(self, stats):
        """Data object for user statistics.

        Parameters
        ----------
        stats : list[datetime]
            A history of user snippet statistics in chronological order.
        """
        self.stats = stats

    def update(self, stat):
        """Update the stats history with a new Stat entry.

        Parameters
        ----------
        stat : Stat
            Stat object to store to the history.
        """
        if stat.end_time is None:
            raise ValueError("stat must be completed before adding to history")
        if self.stats and stat.end_time < self.stats[-1].end_time:
            raise ValueError("stat must occur after the last entry in the history")
        self.stats.append(stat)

    @classmethod
    def load(cls, filename: str):  # TODO: return type of cls
        """Loads stats from the stats pickle file.

        Parameters
        ----------
        filename : str
            File path to loads stats from.

        Returns
        -------
        Stats
            Stats object loaded from pickle.
        """
        with open(filename, "rb") as fi:
            stats = pickle.load(fi)
        return stats

    def save(self, filename: str) -> None:
        """Saves current statistics to the specified pickle file.

        Parameters
        ----------
        filename : str
            File path to save stats to.
        """
        with open(filename, "wb") as fo:
            pickle.dump(self, fo)

    def __getitem__(self, index: int) -> Stat:
        """Get Stat by index.

        Parameters
        ----------
        index : int
            Index of entry.

        Returns
        -------
        Stat
            Stat object stored at that index.
        """
        return self.stats[index]

    def __len__(self) -> int:
        """Get length of Stats."""
        return len(self.stats)

    def __eq__(self, other) -> bool:
        """Check two Stats objects are equal.

        Parameter
        ---------
        other : Stats
            Other Stats object to check equality of.

        Returns
        -------
        bool
            Whether self is equivalent to other.
        """
        return self.stats == other.stats
