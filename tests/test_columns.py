from pathlib import Path

import pytest

from idslab.columns import (
    CANONICAL_FEATURES,
    CIC_DROP_COLUMNS,
    CIC_META_COLUMNS,
    CSE2018_TO_CANONICAL,
    label_family,
)

FIXTURES = Path(__file__).parent / "fixtures"


def header(name):
    return [c.strip() for c in (FIXTURES / name).read_text().strip().split(",")]


def test_2017_header_matches_canonical_features():
    cols = [c for c in header("cic2017_header.csv") if c not in ("Label", "Fwd Header Length.1")]
    assert cols == CANONICAL_FEATURES


def test_2018_mapping_covers_every_column_one_to_one():
    cols = [c for c in header("cse2018_header.csv") if c != "Label" and c not in CIC_META_COLUMNS]
    assert sorted(cols) == sorted(CSE2018_TO_CANONICAL)
    mapped = [CSE2018_TO_CANONICAL[c] for c in cols]
    assert sorted(mapped) == sorted(CANONICAL_FEATURES)
    assert len(set(mapped)) == len(mapped)


def test_2018_wide_file_extra_columns_are_dropped():
    extra = set(header("cse2018_header_84col.csv")) - set(header("cse2018_header.csv"))
    assert extra == {"Flow ID", "Src IP", "Src Port", "Dst IP"}
    assert extra <= set(CIC_DROP_COLUMNS)


@pytest.mark.parametrize("label,family", [
    ("BENIGN", "benign"), ("Benign", "benign"),
    ("DoS Hulk", "dos_hulk"), ("DoS attacks-Hulk", "dos_hulk"),
    ("Web Attack � Brute Force", "web_bruteforce"),
    ("Web Attack \x96 XSS", "web_xss"),
    ("Web Attack � Sql Injection", "web_sqli"),
    ("Brute Force -Web", "web_bruteforce"), ("SQL Injection", "web_sqli"),
    ("FTP-Patator", "ftp_bruteforce"), ("FTP-BruteForce", "ftp_bruteforce"),
    ("SSH-Patator", "ssh_bruteforce"), ("SSH-Bruteforce", "ssh_bruteforce"),
    ("DDoS", "ddos_loit_2017"), ("DDoS attacks-LOIC-HTTP", "ddos_loic_http"),
    ("DDOS attack-HOIC", "ddos_hoic"), ("DDOS attack-LOIC-UDP", "ddos_loic_udp"),
    ("Infiltration", "infiltration"), ("Infilteration", "infiltration"),
    ("DoS slowloris", "dos_slowloris"), ("DoS attacks-Slowloris", "dos_slowloris"),
    ("DoS Slowhttptest", "dos_slowhttptest"),
    ("DoS attacks-SlowHTTPTest", "dos_slowhttptest"),
    ("PortScan", "portscan"), ("Bot", "bot"), ("Heartbleed", "heartbleed"),
])
def test_labels_map_to_families(label, family):
    assert label_family(label) == family


def test_unknown_label_raises():
    with pytest.raises(KeyError):
        label_family("Totally New Attack")
