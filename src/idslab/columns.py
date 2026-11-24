"""Column names and label families for the CIC datasets.

Canonical feature names are the CIC-IDS2017 (MachineLearningCVE) names with
surrounding spaces stripped. CSE-CIC-IDS2018 names are mapped onto them with an
explicit, one-to-one dictionary (no substring replacement, no positions).
"""

import re

# CSE-CIC-IDS2018 name -> canonical (CIC-IDS2017) name. Covers every feature
# column in the 2018 "Processed Traffic Data for ML Algorithms" CSVs.
CSE2018_TO_CANONICAL = {
    "Dst Port": "Destination Port",
    "Flow Duration": "Flow Duration",
    "Tot Fwd Pkts": "Total Fwd Packets",
    "Tot Bwd Pkts": "Total Backward Packets",
    "TotLen Fwd Pkts": "Total Length of Fwd Packets",
    "TotLen Bwd Pkts": "Total Length of Bwd Packets",
    "Fwd Pkt Len Max": "Fwd Packet Length Max",
    "Fwd Pkt Len Min": "Fwd Packet Length Min",
    "Fwd Pkt Len Mean": "Fwd Packet Length Mean",
    "Fwd Pkt Len Std": "Fwd Packet Length Std",
    "Bwd Pkt Len Max": "Bwd Packet Length Max",
    "Bwd Pkt Len Min": "Bwd Packet Length Min",
    "Bwd Pkt Len Mean": "Bwd Packet Length Mean",
    "Bwd Pkt Len Std": "Bwd Packet Length Std",
    "Flow Byts/s": "Flow Bytes/s",
    "Flow Pkts/s": "Flow Packets/s",
    "Flow IAT Mean": "Flow IAT Mean",
    "Flow IAT Std": "Flow IAT Std",
    "Flow IAT Max": "Flow IAT Max",
    "Flow IAT Min": "Flow IAT Min",
    "Fwd IAT Tot": "Fwd IAT Total",
    "Fwd IAT Mean": "Fwd IAT Mean",
    "Fwd IAT Std": "Fwd IAT Std",
    "Fwd IAT Max": "Fwd IAT Max",
    "Fwd IAT Min": "Fwd IAT Min",
    "Bwd IAT Tot": "Bwd IAT Total",
    "Bwd IAT Mean": "Bwd IAT Mean",
    "Bwd IAT Std": "Bwd IAT Std",
    "Bwd IAT Max": "Bwd IAT Max",
    "Bwd IAT Min": "Bwd IAT Min",
    "Fwd PSH Flags": "Fwd PSH Flags",
    "Bwd PSH Flags": "Bwd PSH Flags",
    "Fwd URG Flags": "Fwd URG Flags",
    "Bwd URG Flags": "Bwd URG Flags",
    "Fwd Header Len": "Fwd Header Length",
    "Bwd Header Len": "Bwd Header Length",
    "Fwd Pkts/s": "Fwd Packets/s",
    "Bwd Pkts/s": "Bwd Packets/s",
    "Pkt Len Min": "Min Packet Length",
    "Pkt Len Max": "Max Packet Length",
    "Pkt Len Mean": "Packet Length Mean",
    "Pkt Len Std": "Packet Length Std",
    "Pkt Len Var": "Packet Length Variance",
    "FIN Flag Cnt": "FIN Flag Count",
    "SYN Flag Cnt": "SYN Flag Count",
    "RST Flag Cnt": "RST Flag Count",
    "PSH Flag Cnt": "PSH Flag Count",
    "ACK Flag Cnt": "ACK Flag Count",
    "URG Flag Cnt": "URG Flag Count",
    "CWE Flag Count": "CWE Flag Count",
    "ECE Flag Cnt": "ECE Flag Count",
    "Down/Up Ratio": "Down/Up Ratio",
    "Pkt Size Avg": "Average Packet Size",
    "Fwd Seg Size Avg": "Avg Fwd Segment Size",
    "Bwd Seg Size Avg": "Avg Bwd Segment Size",
    "Fwd Byts/b Avg": "Fwd Avg Bytes/Bulk",
    "Fwd Pkts/b Avg": "Fwd Avg Packets/Bulk",
    "Fwd Blk Rate Avg": "Fwd Avg Bulk Rate",
    "Bwd Byts/b Avg": "Bwd Avg Bytes/Bulk",
    "Bwd Pkts/b Avg": "Bwd Avg Packets/Bulk",
    "Bwd Blk Rate Avg": "Bwd Avg Bulk Rate",
    "Subflow Fwd Pkts": "Subflow Fwd Packets",
    "Subflow Fwd Byts": "Subflow Fwd Bytes",
    "Subflow Bwd Pkts": "Subflow Bwd Packets",
    "Subflow Bwd Byts": "Subflow Bwd Bytes",
    "Init Fwd Win Byts": "Init_Win_bytes_forward",
    "Init Bwd Win Byts": "Init_Win_bytes_backward",
    "Fwd Act Data Pkts": "act_data_pkt_fwd",
    "Fwd Seg Size Min": "min_seg_size_forward",
    "Active Mean": "Active Mean",
    "Active Std": "Active Std",
    "Active Max": "Active Max",
    "Active Min": "Active Min",
    "Idle Mean": "Idle Mean",
    "Idle Std": "Idle Std",
    "Idle Max": "Idle Max",
    "Idle Min": "Idle Min",
}

# The 77 features shared by both datasets, in CIC-IDS2017 file order.
# (CIC-IDS2017 also has "Fwd Header Length.1", an exact duplicate column that
# we drop.)
CANONICAL_FEATURES = [
    "Destination Port", "Flow Duration", "Total Fwd Packets",
    "Total Backward Packets", "Total Length of Fwd Packets",
    "Total Length of Bwd Packets", "Fwd Packet Length Max",
    "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
    "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
    "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
    "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Total",
    "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Total",
    "Bwd IAT Mean", "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags",
    "Bwd PSH Flags", "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length",
    "Bwd Header Length", "Fwd Packets/s", "Bwd Packets/s", "Min Packet Length",
    "Max Packet Length", "Packet Length Mean", "Packet Length Std",
    "Packet Length Variance", "FIN Flag Count", "SYN Flag Count",
    "RST Flag Count", "PSH Flag Count", "ACK Flag Count", "URG Flag Count",
    "CWE Flag Count", "ECE Flag Count", "Down/Up Ratio", "Average Packet Size",
    "Avg Fwd Segment Size", "Avg Bwd Segment Size", "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk", "Fwd Avg Bulk Rate", "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk", "Bwd Avg Bulk Rate", "Subflow Fwd Packets",
    "Subflow Fwd Bytes", "Subflow Bwd Packets", "Subflow Bwd Bytes",
    "Init_Win_bytes_forward", "Init_Win_bytes_backward", "act_data_pkt_fwd",
    "min_seg_size_forward", "Active Mean", "Active Std", "Active Max",
    "Active Min", "Idle Mean", "Idle Std", "Idle Max", "Idle Min",
]

# Chua & Salam's 11 features (RF importance order), used in Step 1.
BASELINE_FEATURES_CIC = [
    "Bwd Packet Length Std", "Average Packet Size", "Max Packet Length",
    "Packet Length Variance", "Packet Length Std", "Avg Bwd Segment Size",
    "Packet Length Mean", "Destination Port", "Init_Win_bytes_forward",
    "Fwd Packet Length Mean", "Init_Win_bytes_backward",
]

# Columns that are dropped from CIC data (identifiers / duplicates).
CIC_DROP_COLUMNS = ["Fwd Header Length.1", "Flow ID", "Src IP", "Src Port", "Dst IP"]

# Kept as metadata, never used as features (CIC-IDS2017 MachineLearningCVE
# has neither, so they cannot be shared features).
CIC_META_COLUMNS = {"Protocol": "protocol", "Timestamp": "timestamp"}

# Label text -> canonical attack family. Keys are the label lower-cased with
# every non-alphanumeric character removed, so encoding damage in the 2017
# web-attack labels ("Web Attack � Brute Force") does not matter.
LABEL_TO_FAMILY = {
    # shared / both years
    "benign": "benign",
    "bot": "bot",
    "infiltration": "infiltration",
    "infilteration": "infiltration",  # 2018 spelling
    # CIC-IDS2017
    "doshulk": "dos_hulk",
    "dosgoldeneye": "dos_goldeneye",
    "dosslowloris": "dos_slowloris",
    "dosslowhttptest": "dos_slowhttptest",
    "ddos": "ddos_loit_2017",
    "portscan": "portscan",
    "ftppatator": "ftp_bruteforce",
    "sshpatator": "ssh_bruteforce",
    "webattackbruteforce": "web_bruteforce",
    "webattackxss": "web_xss",
    "webattacksqlinjection": "web_sqli",
    "heartbleed": "heartbleed",
    # CSE-CIC-IDS2018
    "dosattackshulk": "dos_hulk",
    "dosattacksgoldeneye": "dos_goldeneye",
    "dosattacksslowloris": "dos_slowloris",
    "dosattacksslowhttptest": "dos_slowhttptest",
    "ddosattacksloichttp": "ddos_loic_http",
    "ddosattackhoic": "ddos_hoic",
    "ddosattackloicudp": "ddos_loic_udp",
    "ftpbruteforce": "ftp_bruteforce",
    "sshbruteforce": "ssh_bruteforce",
    "bruteforceweb": "web_bruteforce",
    "bruteforcexss": "web_xss",
    "sqlinjection": "web_sqli",
}

# Step 5e groups for CSE-CIC-IDS2018 families, relative to CIC-IDS2017
# training. Check each against the dataset documentation before relying on it.
FAMILY_GROUPS_2018 = {
    "seen": ["dos_hulk", "dos_goldeneye", "dos_slowloris", "ssh_bruteforce",
             "web_bruteforce", "web_xss", "web_sqli", "ddos_loic_http"],
    "partly_seen": ["bot"],
    "unseen": ["ddos_hoic", "ddos_loic_udp"],
    "label_suspect": ["infiltration", "ftp_bruteforce", "dos_slowhttptest"],
}


def label_key(label):
    return re.sub(r"[^a-z0-9]", "", str(label).lower())


def label_family(label):
    """Map a raw label to its canonical family; raises on unknown labels."""
    key = label_key(label)
    if key not in LABEL_TO_FAMILY:
        raise KeyError(f"unknown label {label!r} (key {key!r})")
    return LABEL_TO_FAMILY[key]
