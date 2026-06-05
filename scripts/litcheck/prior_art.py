#!/usr/bin/env python3
"""prior_art.py -- a METHOD-level prior-art screen (the literature-check gate).

Before dispatching a new search LANE (especially a cross-survey hunt), query
arXiv for the METHOD to see whether a team has already published it. This is the
"literature-check gate" -- it keeps us from:
  (a) spending a night re-deriving a method a funded group already published,
  (b) calling a lane "novel" when it is not, and
  (c) skipping the right front-filter (the published candidate list to dedup against).

It complements -- does not replace -- the OBJECT-level multi-catalogue novelty
gate (scripts/known_objects/). That one answers "is this object known?"; this one
answers "is this method known?".

This is a SCREEN, not an exhaustive search:
  - arXiv only (open, keyless). ADS is more complete but needs ADS_DEV_KEY; a
    future upgrade can add an ADS backend (see TODO at bottom).
  - It surfaces recent matching papers; a human must READ them and judge.
  - Absence of a hit is WEAK evidence of novelty -- pair it with the object-level
    front-filter, and read more before ever claiming "novel".

Usage:
  python scripts/litcheck/prior_art.py "Gaia eROSITA accreting compact binary ZTF"
  python scripts/litcheck/prior_art.py "Fermi unassociated spider millisecond pulsar" --since 2023 --max 12
  python scripts/litcheck/prior_art.py "<method>" --category astro-ph.HE,astro-ph.SR

Exit code 2 on a network/parse failure (so a workflow can distinguish "gate could
not run" from "gate ran, found nothing").
"""
import argparse
import fcntl
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ATOM = "{http://www.w3.org/2005/Atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"
API = "https://export.arxiv.org/api/query"
UA = "gaia-recovered-prior-art/1.0 (solo research; mailto:alexander.keur@gmail.com)"

# --- Cross-process throttle + cache --------------------------------------------
# arXiv asks for ~1 request / 3 s. When many scouts call this gate in parallel (a
# fan-out), naive concurrent requests trip HTTP 429 and arXiv throttles the IP for
# a long window — observed 2026-06-05: a 9-scout fan-out DOSed the gate so it could
# not run at all. The lockfile throttle SERIALIZES requests across processes (each
# caller holds an exclusive lock while it waits out the interval, so N concurrent
# callers fire one-at-a-time instead of racing into a 429), and a small on-disk
# cache means repeated identical queries never re-hit arXiv.
_GATE_DIR = os.path.join(tempfile.gettempdir(), "prior_art_gate")
_LOCK_PATH = os.path.join(_GATE_DIR, "arxiv.lock")
_TS_PATH = os.path.join(_GATE_DIR, "last_request.txt")
_CACHE_PATH = os.path.join(_GATE_DIR, "cache.json")
MIN_INTERVAL = 3.5      # seconds between arXiv requests, enforced across processes
CACHE_TTL = 7 * 86400   # reuse cached results for 7 days


def _throttle():
    """Block until >= MIN_INTERVAL has elapsed since the last request by ANY
    process. Holds an exclusive lock while waiting, so N concurrent callers queue
    and fire one-at-a-time rather than all racing into a 429."""
    os.makedirs(_GATE_DIR, exist_ok=True)
    lf = open(_LOCK_PATH, "w")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        last = 0.0
        try:
            with open(_TS_PATH) as fh:
                last = float(fh.read().strip() or 0)
        except (OSError, ValueError):
            last = 0.0
        wait = MIN_INTERVAL - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        with open(_TS_PATH, "w") as fh:
            fh.write(str(time.time()))
    finally:
        try:
            fcntl.flock(lf, fcntl.LOCK_UN)
        finally:
            lf.close()


def _cache_get(key):
    try:
        with open(_CACHE_PATH) as fh:
            cache = json.load(fh)
    except (OSError, ValueError):
        return None
    entry = cache.get(key)
    if entry and (time.time() - entry.get("t", 0)) < CACHE_TTL:
        return entry.get("xml")
    return None


def _cache_put(key, xml_text):
    os.makedirs(_GATE_DIR, exist_ok=True)
    lf = open(_LOCK_PATH, "w")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        cache = {}
        try:
            with open(_CACHE_PATH) as fh:
                cache = json.load(fh)
        except (OSError, ValueError):
            cache = {}
        cache[key] = {"t": time.time(), "xml": xml_text}
        tmp = _CACHE_PATH + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(cache, fh)
        os.replace(tmp, _CACHE_PATH)
    finally:
        try:
            fcntl.flock(lf, fcntl.LOCK_UN)
        finally:
            lf.close()


def build_query(query, category):
    # AND the whitespace-separated terms, each as a quoted single-token phrase so
    # arXiv binds EVERY term to all: (a bare "all:a b c" binds only "a") and so an
    # internal hyphen ("X-ray") is not read as a NOT operator.
    terms = [t for t in query.split() if t]
    q = " AND ".join('all:"%s"' % t for t in terms)
    if category:
        cats = " OR ".join("cat:" + c.strip() for c in category.split(","))
        q = "(%s) AND (%s)" % (q, cats)
    return q


def search(query, max_results=10, category=None, sort="submittedDate", retries=3,
           throttle=True, cache=True):
    params = {
        "search_query": build_query(query, category),
        "start": 0,
        "max_results": max_results,
        "sortBy": sort,
        "sortOrder": "descending",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    if cache:
        hit = _cache_get(url)
        if hit is not None:
            return hit
    last = None
    for attempt in range(retries):
        try:
            if throttle:
                _throttle()
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read()
            if cache:
                _cache_put(url, raw.decode("utf-8", "replace"))
            return raw
        except urllib.error.HTTPError as ex:
            last = ex
            # arXiv asks for ~1 req / 3 s; on 429 (rate limit) back off harder.
            wait = 15 if ex.code == 429 else 3 * (attempt + 1)
            if attempt < retries - 1:
                time.sleep(wait)
        except Exception as ex:  # noqa: BLE001 -- arXiv API is flaky; retry then give up
            last = ex
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
    raise last


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    total = root.findtext(OPENSEARCH + "totalResults")
    entries = []
    for e in root.findall(ATOM + "entry"):
        title = " ".join((e.findtext(ATOM + "title") or "").split())
        published = (e.findtext(ATOM + "published") or "")[:10]
        summary = " ".join((e.findtext(ATOM + "summary") or "").split())
        authors = [a.findtext(ATOM + "name") for a in e.findall(ATOM + "author")]
        arxiv_id = (e.findtext(ATOM + "id") or "").strip()
        cats = [c.get("term") for c in e.findall(ATOM + "category")]
        entries.append({
            "title": title, "published": published, "summary": summary,
            "authors": authors, "id": arxiv_id, "cats": cats,
        })
    return total, entries


def fmt(total, entries, query):
    out = []
    out.append("# Prior-art screen (arXiv) -- query: %r" % query)
    out.append("# arXiv totalResults ~ %s; showing %d" % (total, len(entries)))
    out.append("")
    if not entries:
        out.append("NO MATCHES in this window -- WEAK evidence of method-novelty")
        out.append("(arXiv-only screen; broaden the query and read more before claiming novel).")
        return "\n".join(out)
    for i, e in enumerate(entries, 1):
        au = ", ".join(a for a in e["authors"][:3] if a)
        if len(e["authors"]) > 3:
            au += " et al."
        snippet = e["summary"][:280] + ("..." if len(e["summary"]) > 280 else "")
        out.append("[%d] %s  %s" % (i, e["published"], e["title"]))
        out.append("     %s" % au)
        out.append("     %s  [%s]" % (e["id"], ", ".join(c for c in e["cats"][:4] if c)))
        out.append("     %s" % snippet)
        out.append("")
    out.append("REMINDER: a hit means the method is (partly) published -> record the ref in")
    out.append("docs/RESEARCH_LOG.md, front-filter candidates against that paper's list, and")
    out.append("frame the lane as method-validation, NOT novel discovery. Absence != novelty.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="arXiv prior-art screen for a search method (the literature-check gate).")
    ap.add_argument("query", help="method description, e.g. 'Gaia eROSITA accreting compact binary ZTF'")
    ap.add_argument("--max", type=int, default=10, help="max results (default 10)")
    ap.add_argument("--since", help="only show hits published on/after this year (e.g. 2023)")
    ap.add_argument("--category", help="restrict to arXiv categories, comma-sep (e.g. astro-ph.HE,astro-ph.SR)")
    ap.add_argument("--relevance", action="store_true", help="sort by relevance instead of newest-first")
    ap.add_argument("--no-throttle", action="store_true", help="disable the cross-process arXiv throttle (only if you are the sole caller)")
    ap.add_argument("--no-cache", action="store_true", help="bypass the on-disk result cache")
    args = ap.parse_args()
    try:
        raw = search(args.query, max_results=args.max, category=args.category,
                     sort="relevance" if args.relevance else "submittedDate",
                     throttle=not args.no_throttle, cache=not args.no_cache)
        total, entries = parse(raw)
    except Exception as ex:  # noqa: BLE001 -- a screen: report and signal "could not run"
        print("prior-art gate FAILED to run (network/parse): %s" % ex, file=sys.stderr)
        sys.exit(2)
    if args.since:
        entries = [e for e in entries if e["published"] >= args.since]
    print(fmt(total, entries, args.query))


if __name__ == "__main__":
    main()

# TODO(optional upgrade): add an ADS backend (export ADS_DEV_KEY) for fuller
# coverage + citation counts; arXiv-only is the keyless default that always runs.
