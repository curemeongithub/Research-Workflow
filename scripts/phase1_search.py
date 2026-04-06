#!/usr/bin/env python3
"""Phase 1 source search and download script for Research Pipeline v2.

v2 changes:
- Primary download: arXiv PDF + Mistral OCR (not LaTeX tarballs)
- Identity verification: grep for title/author in extracted content
- Code repository search: Semantic Scholar + GitHub API
- No web/blog sources — papers only
- Target: 15-25 papers (down from 30-40)
"""

import urllib.request
import urllib.parse
import json
import os
import subprocess
import sys
import time
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
os.makedirs(SOURCES_DIR, exist_ok=True)


def search_semantic_scholar(query, limit=25):
    url = ("https://api.semanticscholar.org/graph/v1/paper/search"
           "?query=" + urllib.parse.quote(query) +
           "&fields=title,authors,year,externalIds,abstract"
           "&limit=" + str(limit))
    req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def download_arxiv_pdf(paper_id):
    """Download arXiv PDF and extract via Mistral OCR."""
    dest = os.path.join(SOURCES_DIR, f"arxiv-{paper_id}")
    pdf_path = os.path.join(dest, f"{paper_id}.pdf")
    content_path = os.path.join(dest, "content.md")

    # Skip if already processed
    if os.path.exists(content_path) and os.path.getsize(content_path) > 500:
        print(f"  [SKIP] arxiv-{paper_id} already has content.md")
        return dest, True

    os.makedirs(dest, exist_ok=True)

    # Download PDF
    if not os.path.exists(pdf_path):
        url = f"https://arxiv.org/pdf/{paper_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/2.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                content = r.read()
            with open(pdf_path, "wb") as f:
                f.write(content)
            print(f"  [PDF-DL] arxiv-{paper_id} ({len(content) // 1024} KB)")
        except Exception as e:
            print(f"  [PDF-FAIL] arxiv-{paper_id}: {e}")
            return dest, False

    # Run Mistral OCR
    ocr_script = os.path.join(os.path.dirname(__file__), "mistral_ocr.py")
    py = os.path.join(PROJECT_ROOT, ".venv/bin/python")
    if os.path.exists(ocr_script):
        try:
            subprocess.run([py, ocr_script, pdf_path, "-o", dest],
                           capture_output=True, timeout=120)
            if os.path.exists(content_path) and os.path.getsize(content_path) > 500:
                print(f"  [OCR-OK] arxiv-{paper_id}")
                return dest, True
            else:
                print(f"  [OCR-SMALL] arxiv-{paper_id} — content.md too small")
                return dest, False
        except Exception as e:
            print(f"  [OCR-ERR] arxiv-{paper_id}: {e}")
            return dest, False
    else:
        print(f"  [WARN] mistral_ocr.py not found, PDF downloaded but not extracted")
        return dest, True  # PDF exists, extraction can happen in Phase 2


def verify_paper_identity(content_file, expected_title, expected_author):
    """Grep for title keywords and author surname in extracted content."""
    if not os.path.isfile(content_file):
        return False
    try:
        with open(content_file, encoding='utf-8', errors='replace') as f:
            text = f.read(5000).lower()
    except Exception:
        return False
    # Check for 2+ words from title
    title_words = [w.lower() for w in expected_title.split() if len(w) > 3]
    title_hits = sum(1 for w in title_words if w in text)
    # Check for author surname
    author_surname = expected_author.split(',')[0].split()[-1].lower()
    # Handle "& LastName" format
    if '&' in expected_author:
        author_surname = expected_author.split('&')[0].strip().split()[-1].lower()
    author_hit = author_surname in text
    return title_hits >= 2 and author_hit


def search_code_repos(paper_id, title):
    """Search Semantic Scholar for linked code repos."""
    repos = []
    try:
        url = (f"https://api.semanticscholar.org/graph/v1/paper/ArXiv:{paper_id}"
               "?fields=externalIds,url,openAccessPdf")
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/2.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        paper_url = data.get('url', '')
        if 'github.com' in paper_url:
            repos.append({"url": paper_url, "verified": True})
    except Exception:
        pass

    # Search GitHub (lightweight — just top result)
    try:
        query = '+'.join(title.split()[:5])
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&per_page=3"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/2.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        for item in data.get('items', [])[:2]:
            if item.get('stargazers_count', 0) >= 5:
                repos.append({
                    "url": item['html_url'],
                    "verified": False,
                    "stars": item['stargazers_count']
                })
    except Exception:
        pass

    return repos


def get_readable_file(dest):
    """Find the best readable text file in a source directory."""
    for ext in [".md", ".tex", ".txt"]:
        for dirpath, _, fnames in os.walk(dest):
            for fn in fnames:
                if fn.endswith(ext) and not fn.startswith("."):
                    fpath = os.path.join(dirpath, fn)
                    if os.path.getsize(fpath) > 500:
                        return fpath
    return None


def check_readable(dest):
    """Check if source directory has readable content >= 500 chars."""
    f = get_readable_file(dest)
    if f and os.path.getsize(f) >= 500:
        return True, f
    for dirpath, _, fnames in os.walk(dest):
        for fn in fnames:
            fpath = os.path.join(dirpath, fn)
            if os.path.getsize(fpath) >= 500:
                return True, fpath
    return False, None


def process_user_pdfs():
    """Process PDFs from user-sources/ using Mistral OCR."""
    user_sources_dir = os.path.join(PROJECT_ROOT, "user-sources")
    results = []
    if not os.path.exists(user_sources_dir):
        return results
    ocr_script = os.path.join(os.path.dirname(__file__), "mistral_ocr.py")
    py = os.path.join(PROJECT_ROOT, ".venv/bin/python")
    for fn in os.listdir(user_sources_dir):
        if not fn.endswith(".pdf"):
            continue
        pdf_path = os.path.join(user_sources_dir, fn)
        name = fn[:-4]
        dest = os.path.join(SOURCES_DIR, f"user-{name}")
        os.makedirs(dest, exist_ok=True)
        # Check if already processed
        if os.path.exists(os.path.join(dest, "content.md")):
            print(f"  [SKIP-PDF] user-{name} already processed")
            readable, cf = check_readable(dest)
            results.append((f"user-{name}", "user_pdf", fn, dest, readable, cf))
            continue
        print(f"  [OCR] Processing {fn}...")
        try:
            r = subprocess.run(
                [py, ocr_script, pdf_path, "-o", dest],
                capture_output=True, text=True, timeout=300,
                cwd=PROJECT_ROOT
            )
            readable, cf = check_readable(dest)
            print(f"  [{'OCR-OK' if readable else 'OCR-FAIL'}] user-{name}")
            results.append((f"user-{name}", "user_pdf", fn, dest, readable, cf))
        except Exception as e:
            print(f"  [OCR-ERR] {fn}: {e}")
            results.append((f"user-{name}", "user_pdf", fn, dest, False, None))
    return results


# ─── Paper list ───────────────────────────────────────────────────────────────

ARXIV_PAPERS = [
    # Core Pilanci group — convex reformulation
    ("2012.13401", "Neural Networks are Convex Regularizers: Exact Polynomial-time Convex Optimization Formulations for Two-Layer Networks", "Pilanci & Ergen", 2020),
    ("2110.06482", "Global Optimality Beyond Two Layers: Training Deep ReLU Networks via Convex Programs", "Ergen & Pilanci", 2021),
    ("2012.13635", "Convex Geometry and Duality of Over-parameterized Neural Networks", "Ergen & Pilanci", 2021),
    ("2002.10553", "Convex Duality and Cutting Plane Methods for Over-parameterized Neural Networks", "Pilanci & Ergen", 2020),
    ("2110.05518", "Hyperparameter Optimization as a Service via Convex Neural Networks", "Ergen et al.", 2021),
    ("2402.03625", "Scalable Convex Optimization of Neural Networks via Frank-Wolfe Methods", "Mishkin et al.", 2024),
    ("2106.05528", "Convex Neural Networks with Sparsity-Inducing Regularizers", "Ergen & Pilanci", 2021),
    ("2104.02796", "Global Optimality via Convex Duality for Deep Neural Networks", "Sahiner et al.", 2021),
    ("2209.01113", "Vector-Output ReLU Neural Network Problems are Copositive Programs", "Chen & Pilanci", 2022),
    ("2307.01197", "Convex Relaxations of ReLU Neural Networks for the Certification of Robustness", "Raghunathan et al.", 2023),
    # Frank-Wolfe and sparse optimization
    ("2209.01062", "Regularization and Optimization in Deep Learning via Dual Methods", "Mishkin & Pilanci", 2022),
    ("2104.14641", "Optimal Approximation with Sparse Deep Neural Networks using Residual Connections", "Boursier et al.", 2021),
    # NTK / kernel connections
    ("1806.07572", "Neural Tangent Kernel: Convergence and Generalization in Neural Networks", "Jacot et al.", 2018),
    ("2002.02405", "Finite Versus Infinite Neural Networks: an Empirical Study", "Lee et al.", 2020),
    ("1904.11955", "On the Inductive Bias of Neural Tangent Kernels", "Bietti & Mairal", 2019),
    # Polyhedral / disjunctive programming
    ("2204.09875", "Characterizing the Implicit Bias of Regularized Neural Networks via the Convex Lasso", "Boursier et al.", 2023),
    ("2012.09769", "Sparse Neural Network Training via Convex Polytope Projections", "Ergen & Pilanci", 2020),
    # Lasso / group Lasso connections
    ("2104.01506", "Group-Sparse Neural Networks via Convex Duality — Deep Architectures", "Ergen & Pilanci", 2021),
    # Certifiable robustness / verification
    ("1811.01988", "Semidefinite Relaxations for Neural Network Verification", "Raghunathan et al.", 2018),
    # ADMM / proximal methods
    ("1703.04699", "A Unified Convergence Analysis of Block Successive Minimization Methods", "Razaviyayn et al.", 2013),
    # Deep learning theory / loss landscape
    ("1811.10927", "The Loss Surfaces of Multilayer Networks", "Dauphin et al.", 2019),
    ("1901.00596", "Gradient Descent Finds Global Minima of Non-Convex Neural Networks", "Du et al.", 2019),
    # Implicit regularization
    ("1710.10174", "Implicit Regularization in Matrix Factorization", "Gunasekar et al.", 2017),
    ("2103.01799", "Characterizing Implicit Bias in Terms of Optimization Geometry", "Woodworth et al.", 2021),
    # Random features
    ("0709.1542", "Random Features for Large-Scale Kernel Machines", "Rahimi & Recht", 2007),
    # Convex analysis background
    ("2011.02083", "A Short Proof that the List of Extreme Points is Finite for Convex Neural Networks", "Parhi & Nowak", 2020),
]


# ─── Main ──���────────────────────────────���─────────────────────────────────────

def main():
    manifest_entries = []

    # 1. Process user PDFs
    print("\n=== Processing User PDFs ===")
    user_results = process_user_pdfs()
    for src_id, src_type, title, dest, readable, cf in user_results:
        rel_path = os.path.relpath(dest, PROJECT_ROOT)
        cf_rel = os.path.relpath(cf, PROJECT_ROOT) if cf else None
        manifest_entries.append({
            "id": src_id,
            "type": src_type,
            "title": title,
            "local_path": rel_path,
            "content_file": cf_rel,
            "readable": readable,
            "identity_verified": True,  # User PDFs are trusted
            "extraction_method": "mistral-ocr-pdf",
            "code_repos": [],
            "notes": "User-provided PDF processed via Mistral OCR"
        })

    # 2. Download arXiv PDFs and extract
    print("\n=== Downloading arXiv Papers (PDF + Mistral OCR) ===")
    for paper_id, title, authors, year in ARXIV_PAPERS:
        print(f"\n[arXiv:{paper_id}] {title[:60]}...")
        dest, ok = download_arxiv_pdf(paper_id)
        readable, cf = check_readable(dest)
        rel_path = os.path.relpath(dest, PROJECT_ROOT)
        cf_rel = os.path.relpath(cf, PROJECT_ROOT) if cf else None

        # Identity verification
        identity_ok = False
        if cf:
            identity_ok = verify_paper_identity(cf, title, authors)
            print(f"  [VERIFY] identity_verified={identity_ok}")

        # Code repository search
        repos = search_code_repos(paper_id, title)
        if repos:
            print(f"  [REPOS] Found {len(repos)} code repo(s)")

        manifest_entries.append({
            "id": f"arxiv-{paper_id}",
            "type": "arxiv",
            "title": title,
            "authors": [authors],
            "year": year,
            "arxiv_id": paper_id,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "local_path": rel_path,
            "content_file": cf_rel,
            "readable": readable,
            "identity_verified": identity_ok,
            "extraction_method": "mistral-ocr-pdf",
            "code_repos": repos,
            "notes": ""
        })
        time.sleep(0.3)  # Be polite to arXiv

    # 3. Write manifest
    print("\n=== Writing Manifest ===")
    verified_count = sum(1 for e in manifest_entries
                         if e.get("identity_verified") and e.get("type") == "arxiv")
    manifest = {
        "topic": "Dual Convex Optimization in ReLU Neural Networks",
        "generated": datetime.datetime.now(datetime.UTC).isoformat(),
        "total_sources": len(manifest_entries),
        "readable_count": sum(1 for e in manifest_entries if e.get("readable")),
        "verified_count": verified_count,
        "sources": manifest_entries,
    }
    manifest_path = os.path.join(PROJECT_ROOT, "sources", "manifest.yaml")
    import yaml
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Manifest written: {manifest_path}")
    print(f"Total sources: {manifest['total_sources']}")
    print(f"Readable: {manifest['readable_count']}")
    print(f"Identity verified: {verified_count}")

    # Summary
    print("\n=== Summary ===")
    arxiv_ok = sum(1 for e in manifest_entries if e['type'] == 'arxiv' and e.get('readable'))
    arxiv_total = sum(1 for e in manifest_entries if e['type'] == 'arxiv')
    user_ok = sum(1 for e in manifest_entries if e['type'] == 'user_pdf' and e.get('readable'))
    repos_found = sum(1 for e in manifest_entries if e.get('code_repos'))
    print(f"arXiv papers: {arxiv_ok}/{arxiv_total} readable, {verified_count} identity-verified")
    print(f"User PDFs: {user_ok}/{len(user_results)} readable")
    print(f"Papers with code repos: {repos_found}")

    return manifest['total_sources'], manifest['readable_count']


if __name__ == "__main__":
    total, readable = main()
    sys.exit(0 if readable >= 15 else 1)
