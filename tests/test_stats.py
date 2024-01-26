import os
import time
from datetime import datetime

import pytest

from lpm.stats import (
    Stat,
    Stats,
    accuracy,
    characters_per_minute,
    lines_per_minute,
    words_per_minute,
)


def test_Stat():
    stat = Stat()

    stat.start()
    time.sleep(2)
    stat.stop()
    assert stat.elapsed == pytest.approx(2, 0.01)

    stat.num_chars += 25
    stat.num_lines += 3
    stat.num_correct += 70
    stat.num_wrong += 30

    expected_cpm = 60 * 25 / 2
    expected_wpm = 60 * (25 / 5.6) / 2
    expected_lpm = 60 * 3 / 2
    expected_acc = 0.7

    assert stat.cpm == pytest.approx(expected_cpm, 0.01)
    assert stat.wpm == pytest.approx(expected_wpm, 0.01)
    assert stat.lpm == pytest.approx(expected_lpm, 0.01)
    assert stat.acc == pytest.approx(expected_acc, 0.01)


def test_Stats():
    fmt = "%Y-%m-%d %H:%M:%S"

    # 10 second difference
    stat1 = Stat(
        start_time=datetime.strptime("2020-01-02 16:12:11", fmt),
        end_time=datetime.strptime("2020-01-02 16:12:21", fmt),
    )

    # 1 hour 3 minutes and 15 second difference
    stat2 = Stat(
        start_time=datetime.strptime("2020-01-02 17:12:11", fmt),
        end_time=datetime.strptime("2020-01-02 18:15:25", fmt),
    )

    # one day difference
    stat3 = Stat(
        start_time=datetime.strptime("2020-01-02 09:12:11", fmt),
        end_time=datetime.strptime("2020-01-03 09:12:11", fmt),
    )

    stats = Stats([stat1, stat2])
    assert len(stats) == 2
    stats.update(stat3)
    assert len(stats) == 3

    # no end or start time
    with pytest.raises(ValueError):
        stats.update(Stat())

    # no end time
    with pytest.raises(ValueError):
        stats.update(Stat(datetime.strptime("2020-01-02 16:12:11", fmt)))

    # update list with datetime that is older than last entry
    with pytest.raises(ValueError):
        stats.update(stat1)

    filename = ".deleteme"
    stats.save(filename)
    assert stats == stats.load(filename)
    os.remove(filename)


def test_S1():
    """Test lines per minute calculation."""
    assert lines_per_minute(1, 10) == 6
    assert lines_per_minute(2, 10) == 12
    assert lines_per_minute(0, 10) == 0


def test_S2():
    """Test characters per minute calculation."""
    assert characters_per_minute(20, 5) == 240
    assert characters_per_minute(0, 10) == 0


def test_S3():
    """Test words per minute calculation."""
    assert words_per_minute(5.6 * 10, 10) == 60
    assert words_per_minute(0, 10) == 0


def test_S4():
    """Test accuracy calculations."""
    assert accuracy(100, 0) == 1
    assert accuracy(99, 1) == 0.99
    assert accuracy(0, 100) == 0


def test_S5():
    """Test lifetime statistics."""
    import statistics

    fmt = "%Y-%m-%d %H:%M:%S"

    # 10 second difference
    stat1 = Stat(
        start_time=datetime.strptime("2020-01-02 16:12:11", fmt),
        end_time=datetime.strptime("2020-01-02 16:12:21", fmt),
    )
    stat1.num_lines += 3

    # 10 second difference
    stat2 = Stat(
        start_time=datetime.strptime("2020-02-02 16:12:11", fmt),
        end_time=datetime.strptime("2020-02-02 16:12:21", fmt),
    )
    stat2.num_lines += 4

    stats = Stats([])
    stats.update(stat1)
    stats.update(stat2)

    assert statistics.mean([stat.lpm for stat in stats.stats]) == 21
