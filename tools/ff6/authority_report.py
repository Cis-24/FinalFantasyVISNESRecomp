"""Short authority-pipeline report (<= 40 lines): export, audit, AOT count vs baseline."""
import argparse
import json
from collections import Counter
from pathlib import Path


def dispositions(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Counter(n.get("disposition", "?") for n in d["nodes"].values()), d


def top_reasons(manifest, n=6):
    c = Counter(r for v in manifest["nodes"].values() for r in v.get("reasons", [])
                if not r.startswith(("authority_conflict_at_", "bad_")))
    return c.most_common(n)


def main():
    ap = argparse.ArgumentParser()
    for k in ("export", "audit", "manifest", "baseline"):
        ap.add_argument("--" + k, required=True, type=Path)
    a = ap.parse_args()
    out = ["-- export --"] + a.export.read_text(encoding="utf-8").splitlines()[:9]
    audit = json.loads(a.audit.read_text(encoding="utf-8"))
    out.append("-- audit --")
    for k in ("observed_variants", "invalid_variants", "variants_with_unknown_instructions",
              "authority_instructions", "covered_authority_instructions"):
        out.append(f"{k}: {audit.get(k)}")
    out.append(f"instruction classes: {audit.get('instruction_instances_by_class')}")
    out.append(f"failure classes: {audit.get('variants_by_failure_class')}")
    cand, cm = dispositions(a.manifest)
    base, _ = dispositions(a.baseline)
    out.append("-- AOT (program_manifest) --")
    out.append(f"baseline nodes {sum(base.values())}: {dict(base)}")
    out.append(f"candidate nodes {sum(cand.values())}: {dict(cand)}")
    out.append(f"aot_eligible: {base.get('aot_eligible', 0)} -> {cand.get('aot_eligible', 0)}")
    out.append("top reasons: " + ", ".join(f"{r}={n}" for r, n in top_reasons(cm)))
    print("\n".join(out[:40]))


if __name__ == "__main__":
    main()
