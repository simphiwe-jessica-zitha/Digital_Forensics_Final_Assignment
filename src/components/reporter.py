import csv
import io
from datetime import datetime

def _timestamp() -> str:
    """Return a human-readable timestamp for the report header."""
    return datetime.now().strftime("%Y-%m-%d  %H:%M:%S")


def _divider(char: str = "─", width: int = 60) -> str:
    return char * width


#TXT report

def generate_txt_report(query: str, result: dict) -> str:
    """
    Build a plain-text forensic investigation report.

    Parameters
    ----------
    query  : the original search query string
    result : the dict returned by run_search()
              keys used → error, match_count, evidence
              each evidence item → original_name, file_type,
                                   matched_tokens, match_count, score

    Returns
    -------
    str : full report as a single string (ready for st.download_button)
    """
    lines = []

    #Cover block
    lines.append(_divider("═"))
    lines.append("  FORENSIC AI — KEYWORD SEARCH INVESTIGATION REPORT")
    lines.append(_divider("═"))
    lines.append(f"  Generated  : {_timestamp()}")
    lines.append(f"  Query      : {query}")
    lines.append(f"  Status     : {'ERROR' if result.get('error') else 'COMPLETE'}")
    lines.append(_divider("═"))
    lines.append("")

    #Error case
    if result.get("error"):
        lines.append(f"  ERROR: {result['error']}")
        lines.append("")
        return "\n".join(lines)

    evidence    = result.get("evidence", [])
    match_count = result.get("match_count", 0)

    #Summary block
    lines.append("SUMMARY")
    lines.append(_divider())
    lines.append(f"  Total documents matched  : {match_count}")

    if evidence:
        top = evidence[0]
        lines.append(f"  Highest-scoring file     : {top['original_name']}")
        lines.append(f"  Top score                : {top['score']:.4f}")

        all_keywords: set = set()
        for m in evidence:
            all_keywords.update(m["matched_tokens"].keys())
        lines.append(f"  Unique keywords hit      : {len(all_keywords)}")
        lines.append(f"  Keywords                 : {', '.join(sorted(all_keywords))}")
    else:
        lines.append("  No matching documents were found for this query.")

    lines.append("")

    #Ranked results
    if evidence:
        lines.append("RANKED RESULTS")
        lines.append(_divider())
        lines.append(
            f"  {'#':<4} {'File':<35} {'Type':<10} {'Hits':<6} {'Score':<8}  Keywords Found"
        )
        lines.append(
            f"  {'─'*4} {'─'*35} {'─'*10} {'─'*6} {'─'*8}  {'─'*20}"
        )

        for i, m in enumerate(evidence, start=1):
            keywords_str = ", ".join(m["matched_tokens"].keys())
            lines.append(
                f"  {i:<4} "
                f"{m['original_name']:<35} "
                f"{m['file_type']:<10} "
                f"{m['match_count']:<6} "
                f"{m['score']:<8.4f}  "
                f"{keywords_str}"
            )

        lines.append("")

        #Per-document detail
        lines.append("DOCUMENT DETAIL")
        lines.append(_divider())

        for i, m in enumerate(evidence, start=1):
            lines.append(f"\n  [{i}]  {m['original_name']}")
            lines.append(f"       Type       : {m['file_type']}")
            lines.append(f"       Score      : {m['score']:.4f}")
            lines.append(f"       Total hits : {m['match_count']}")
            lines.append(f"       Keywords matched:")

            for kw, count in m["matched_tokens"].items():
                lines.append(f"           • {kw}  ({count} occurrence{'s' if count != 1 else ''})")

    lines.append("")
    lines.append(_divider("═"))
    lines.append("  END OF REPORT")
    lines.append(_divider("═"))

    return "\n".join(lines)


#CSV report

def generate_csv_report(query: str, result: dict) -> str:
    """
    Build a CSV export of search results, suitable for spreadsheet analysis.

    Returns
    -------
    str : CSV content as a string (ready for st.download_button)
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Metadata rows at the top (prefixed with #)
    writer.writerow(["# FORENSIC AI — SEARCH RESULTS EXPORT"])
    writer.writerow(["# Generated", _timestamp()])
    writer.writerow(["# Query", query])
    writer.writerow([])

    # Column headers
    writer.writerow([
        "Rank",
        "File Name",
        "File Type",
        "Match Count",
        "Score",
        "Keywords Found",
        "Keyword Occurrences",
    ])

    evidence = result.get("evidence", [])
    for i, m in enumerate(evidence, start=1):
        keywords      = ", ".join(m["matched_tokens"].keys())
        kw_detail     = " | ".join(
            f"{kw}:{cnt}" for kw, cnt in m["matched_tokens"].items()
        )
        writer.writerow([
            i,
            m["original_name"],
            m["file_type"],
            m["match_count"],
            f"{m['score']:.4f}",
            keywords,
            kw_detail,
        ])

    return output.getvalue()


#Filename helpers

def report_filename(query: str, ext: str) -> str:
    """
    Generate a safe filename for the report based on the query.
    e.g.  "money laundering"  →  "forensic_report_money_laundering.txt"
    """
    safe = query.strip().lower()
    safe = "".join(c if c.isalnum() or c == " " else "" for c in safe)
    safe = "_".join(safe.split())[:40]          # max 40 chars
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"forensic_report_{safe}_{stamp}.{ext}"
