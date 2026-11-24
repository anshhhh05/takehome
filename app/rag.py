"""Small deterministic stand-in for a document answer service, intentionally imperfect.

It extracts simple known phrases instead of using an LLM. Contract tests should
be repeatable, with no internet access or API key.
"""
from __future__ import annotations
import re


def get_metric_value(doc: dict, metric: str) -> int | None:
    text = doc["extracted_text"]
    pattern = (
        r"Orders\s+completed:\s*([\d,]+)" if metric == "orders_completed"
        else r"Support\s+tickets\s+received:\s*([\d,]+)"
    )
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else None


def insufficient() -> dict:
    return {"status": "insufficient_evidence",
            "answer": "Insufficient evidence in the selected documents.",
            "facts": None, "citations": []}


def resolve_question(question: str, docs: list[dict]) -> dict:
    """Return simulated answers. The implementation is intentionally imperfect."""
    question_lower = question.lower()
    if "order" in question_lower:
        metric = "orders_completed"
    elif "ticket" in question_lower:
        metric = "support_tickets"
    else:
        return insufficient()
    if not docs:
        return insufficient()

    explicit_years = [int(y) for y in re.findall(r"fy\s*(20\d{2})", question_lower)]
    is_comparison = len(set(explicit_years)) >= 2 and any(
        term in question_lower for term in ("change", "compare", "vs", "versus", "from")
    )
    if is_comparison:
        baseline_year, target_year = min(explicit_years), max(explicit_years)
        target_doc = next((d for d in docs if d["fiscal_year"] == target_year), None)
        baseline_doc = next((d for d in docs if d["fiscal_year"] == baseline_year), None)
        if target_doc is None or baseline_doc is None:
            return insufficient()
        target_value = get_metric_value(target_doc, metric)
        baseline_value = get_metric_value(baseline_doc, metric)
        if target_value is None or baseline_value is None or baseline_value == 0:
            return insufficient()
        # This is the supplied implementation, not the acceptance oracle.
        change_pct = round((target_value - baseline_value) / target_value * 100, 2)
        return {"status": "success",
                "answer": f"{metric.replace('_',' ')} changed by {change_pct:+.2f}% from FY{baseline_year} ({baseline_value}) to FY{target_year} ({target_value}).",
                "facts": {"metric": metric, "fiscal_year": target_year, "value": target_value,
                          "baseline_year": baseline_year, "baseline_value": baseline_value,
                          "change_pct": change_pct},
                "citations": [{"document_id": docs[0]["id"], "page": docs[0]["page"]}]}

    requested_year = explicit_years[-1] if explicit_years else None
    chosen_doc = max(docs, key=lambda d: d["fiscal_year"]) if requested_year is None else docs[0]
    value = get_metric_value(chosen_doc, metric)
    if value is None:
        return insufficient()
    return {"status": "success",
            "answer": f"{metric.replace('_',' ')} were {value} in FY{chosen_doc['fiscal_year']}.",
            "facts": {"metric": metric, "fiscal_year": chosen_doc["fiscal_year"], "value": value,
                      "baseline_year": None, "baseline_value": None, "change_pct": None},
            "citations": [{"document_id": chosen_doc["id"], "page": chosen_doc["page"]}]}
