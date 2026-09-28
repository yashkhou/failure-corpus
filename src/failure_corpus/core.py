from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import re


@dataclass
class Failure:
    framework: str
    test: str
    message: str
    context: str
    fingerprint: str = ""
    count: int = 1

    def as_dict(self):
        return asdict(self)


def normalize(text: str) -> str:
    text = re.sub(r"\b\d{4}-\d\d-\d\d[T ][0-9:.+\-Z]+\b", "<time>", text)
    text = re.sub(r"(/[^\s:]+)+", "<path>", text)
    text = re.sub(r":\d+(?::\d+)?", ":<line>", text)
    text = re.sub(r"\b0x[0-9a-fA-F]+\b", "<addr>", text)
    text = re.sub(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}\b", "<uuid>", text)
    return re.sub(r"\s+", " ", text).strip()


def _failure(framework: str, test: str, message: str, context: str) -> Failure:
    key = normalize(f"{framework}|{test}|{message}")
    return Failure(framework, test, message, context, hashlib.sha256(key.encode()).hexdigest()[:16])


def parse(text: str) -> list[Failure]:
    out: list[Failure] = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        framework = "generic"
        test = "unknown"
        message = None
        if line.startswith("FAILED "):
            framework = "pytest"
            rest = line[7:]
            test = rest.split(" - ", 1)[0]
            message = rest.split(" - ", 1)[1] if " - " in rest else rest
        elif re.match(r"\s*●\s+", line):
            framework = "jest"
            test = re.sub(r"^\s*●\s+", "", line).strip()
            message = lines[i + 1].strip() if i + 1 < len(lines) else test
        elif line.startswith("--- FAIL: "):
            framework = "go"
            test = line[len("--- FAIL: ") :].split(" ", 1)[0]
            message = next((x.strip() for x in lines[i + 1 : i + 4] if x.strip()), line.strip())
        elif re.match(r"thread ['\"].+['\"] panicked at", line):
            framework = "rust"
            match = re.match(r"thread ['\"](.+?)['\"] panicked at", line)
            test = match.group(1) if match else "unknown"
            message = line.strip()
        elif re.search(r"\b(ERROR|Exception|AssertionError)\b", line):
            message = line.strip()
        if message:
            context = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 3)])
            out.append(_failure(framework, test, message, context))
    return out


def dedupe(records):
    grouped = {}
    for record in records:
        if record.fingerprint in grouped:
            grouped[record.fingerprint].count += record.count
        else:
            grouped[record.fingerprint] = record
    return list(grouped.values())


def shape_signature(record: Failure) -> set[str]:
    text = normalize(record.message.lower())
    text = re.sub(r"(['\"]).*?\1", " <quoted> ", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", " <num> ", text)
    return set(re.findall(r"[a-z_<>]+", text))


def cluster(records, threshold: float = 0.65):
    """Greedily group near-duplicate failures while retaining exact fingerprints."""
    groups: list[dict] = []
    for record in records:
        signature = shape_signature(record)
        match = None
        for group in groups:
            base = group["signature"]
            score = len(signature & base) / max(1, len(signature | base))
            if score >= threshold:
                match = group
                break
        if match is None:
            groups.append({"representative": record, "signature": signature, "members": [record]})
        else:
            match["members"].append(record)
    return [
        {
            "representative": group["representative"].as_dict(),
            "fingerprints": [item.fingerprint for item in group["members"]],
            "occurrences": sum(item.count for item in group["members"]),
        }
        for group in groups
    ]
