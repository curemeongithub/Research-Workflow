#!/usr/bin/env python3
"""Phase 1 source search and download script for Research Pipeline."""

import urllib.request
import urllib.parse
import json
import os
import subprocess
import sys
import time
import datetime
import tarfile
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
os.makedirs(SOURCES_DIR, exist_ok=True)


def search_semantic_scholar(query, limit=20):
    url = ("https://api.semanticscholar.org/graph/v1/paper/search"
           "?query=" + urllib.parse.quote(query) +
           "&fields=title,authors,year,externalIds,abstract"
           "&limit=" + str(limit))
    req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def download_arxiv_source(paper_id):
    """Download and extract arXiv LaTeX source tarball."""
    dest = os.path.join(SOURCES_DIR, f"arxiv-{paper_id}")
    if os.path.exists(dest) and os.listdir(dest):
        print(f"  [SKIP] arxiv-{paper_id} already exists")
        return dest, True
    os.makedirs(dest, exist_ok=True)
    url = f"https://arxiv.org/src/{paper_id}"
    tarpath = os.path.join(dest, "source.tar.gz")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            with open(tarpath, "wb") as f:
                f.write(r.read())
        # Try to extract
        try:
            with tarfile.open(tarpath, "r:gz") as tar:
                tar.extractall(dest)
            os.remove(tarpath)
        except Exception:
            pass  # May be a single PDF, keep the file
        size = sum(os.path.getsize(os.path.join(dp, fn))
                   for dp, _, fns in os.walk(dest) for fn in fns)
        print(f"  [OK] arxiv-{paper_id} ({size // 1024} KB)")
        return dest, True
    except Exception as e:
        print(f"  [FAIL] arxiv-{paper_id}: {e}")
        return dest, False


def download_arxiv_pdf(paper_id):
    """Download arXiv PDF as fallback."""
    dest = os.path.join(SOURCES_DIR, f"arxiv-{paper_id}")
    os.makedirs(dest, exist_ok=True)
    pdf_path = os.path.join(dest, f"{paper_id}.pdf")
    if os.path.exists(pdf_path):
        print(f"  [SKIP-PDF] arxiv-{paper_id} PDF already exists")
        return dest, True
    url = f"https://arxiv.org/pdf/{paper_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchPipeline/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            content = r.read()
        with open(pdf_path, "wb") as f:
            f.write(content)
        # Run OCR
        ocr_script = os.path.join(os.path.dirname(__file__), "mistral_ocr.py")
        py = os.path.join(PROJECT_ROOT, ".venv/bin/python")
        if os.path.exists(ocr_script):
            subprocess.run([py, ocr_script, pdf_path, "-o", dest],
                           capture_output=True, timeout=120)
        print(f"  [PDF-OK] arxiv-{paper_id}")
        return dest, True
    except Exception as e:
        print(f"  [PDF-FAIL] arxiv-{paper_id}: {e}")
        return dest, False


def get_readable_file(dest):
    """Find the best readable text file in a source directory."""
    # Prefer .tex files, then .md, then .txt
    for ext in [".tex", ".md", ".txt"]:
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
    # Check any file
    for dirpath, _, fnames in os.walk(dest):
        for fn in fnames:
            fpath = os.path.join(dirpath, fn)
            if os.path.getsize(fpath) >= 500:
                return True, fpath
    return False, None


def download_web_source(url, label=None):
    """Download a web page using authenticated_extract.py."""
    script = os.path.join(os.path.dirname(__file__), "authenticated_extract.py")
    py = os.path.join(PROJECT_ROOT, ".venv/bin/python")
    try:
        result = subprocess.run(
            [py, script, url],
            capture_output=True, text=True, timeout=120,
            cwd=PROJECT_ROOT
        )
        # Find the output dir (look for sources/ subdirectory created)
        # The script auto-derives from URL
        parsed = urllib.parse.urlparse(url)
        path_slug = parsed.netloc + parsed.path.rstrip("/")
        candidate = os.path.join(SOURCES_DIR, path_slug)
        if os.path.exists(candidate):
            readable, f = check_readable(candidate)
            print(f"  [WEB-{'OK' if readable else 'FAIL'}] {label or url[:60]}")
            return candidate, readable
        # Try to find by scanning sources/
        print(f"  [WEB-?] {label or url[:60]} — may need manual check")
        return None, False
    except Exception as e:
        print(f"  [WEB-ERR] {label or url[:60]}: {e}")
        return None, False


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
    # Second-order methods
    ("2105.09206", "Randomized Subspace Newton with Variance Reduction and Reduced Communication", "Gower et al.", 2021),
    # Implicit regularization
    ("1710.10174", "Implicit Regularization in Matrix Factorization", "Gunasekar et al.", 2017),
    ("2103.01799", "Characterizing Implicit Bias in Terms of Optimization Geometry", "Woodworth et al.", 2021),
    # Sparse recovery / compressed sensing connections
    ("1907.11714", "Gradient Descent with Early Stopping is Provably Robust to Label Noise for Overparameterized Neural Networks", "Li et al.", 2020),
    # Mixed-integer / ReLU-exact formulations
    ("1711.07576", "Bounding the Optimal Value of a Mixed-Integer Neural Network via Linear Programming", "Anderson et al.", 2020),
    # Random features
    ("0709.1542", "Random Features for Large-Scale Kernel Machines", "Rahimi & Recht", 2007),
    # Convex analysis background
    ("2011.02083", "A Short Proof that the List of Extreme Points is Finite for Convex Neural Networks", "Parhi & Nowak", 2020),
    ("2012.12965", "Banach Space Representer Theorems for Neural Networks and Ridge Splines", "Parhi & Nowak", 2021),
]

# WEB_SOURCES = [
#     ("https://lilianweng.github.io/posts/2022-09-08-ntk/", "Lilian Weng — NTK Blog Post"),
#     ("https://distill.pub/2021/gnn-intro/", "Distill — GNN Intro (convex perspective)"),
#     ("https://francisbach.com/kernel-methods/", "Francis Bach — Kernel Methods Blog"),
# ]

# ─── Main ─────────────────────────────────────────────────────────────────────

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
            "notes": "User-provided PDF processed via Mistral OCR"
        })

    # 2. Download arXiv sources
    print("\n=== Downloading arXiv Sources ===")
    for paper_id, title, authors, year in ARXIV_PAPERS:
        print(f"\n[arXiv:{paper_id}] {title[:60]}...")
        dest, ok = download_arxiv_source(paper_id)
        if not ok:
            print(f"  -> Trying PDF fallback...")
            dest, ok = download_arxiv_pdf(paper_id)
        readable, cf = check_readable(dest)
        rel_path = os.path.relpath(dest, PROJECT_ROOT)
        cf_rel = os.path.relpath(cf, PROJECT_ROOT) if cf else None
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
            "notes": "LaTeX source tarball" if ok else "Download failed"
        })
        time.sleep(0.3)  # Be polite to arXiv

    # # 3. Download web sources
    # print("\n=== Downloading Web Sources ===")
    # for url, label in WEB_SOURCES:
    #     print(f"\n[WEB] {label}...")
    #     dest, readable = download_web_source(url, label)
    #     if dest:
    #         rel_path = os.path.relpath(dest, PROJECT_ROOT)
    #         _, cf = check_readable(dest)
    #         cf_rel = os.path.relpath(cf, PROJECT_ROOT) if cf else None
    #         manifest_entries.append({
    #             "id": label.lower().replace(" ", "-").replace("/", "-")[:40],
    #             "type": "blog",
    #             "title": label,
    #             "url": url,
    #             "local_path": rel_path,
    #             "content_file": cf_rel,
    #             "readable": readable,
    #             "notes": "Web blog/article"
    #         })

    # 4. Write manifest
    print("\n=== Writing Manifest ===")
    manifest = {
        "topic": "Dual Convex Optimization in ReLU Neural Networks",
        "generated": datetime.datetime.now(datetime.UTC).isoformat(),
        "total_sources": len(manifest_entries),
        "readable_count": sum(1 for e in manifest_entries if e.get("readable")),
        "sources": manifest_entries,
    }
    manifest_path = os.path.join(PROJECT_ROOT, "sources", "manifest.yaml")
    import yaml
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Manifest written: {manifest_path}")
    print(f"Total sources: {manifest['total_sources']}")
    print(f"Readable: {manifest['readable_count']}")

    # Summary
    print("\n=== Summary ===")
    arxiv_ok = sum(1 for e in manifest_entries if e['type'] == 'arxiv' and e.get('readable'))
    arxiv_total = sum(1 for e in manifest_entries if e['type'] == 'arxiv')
    user_ok = sum(1 for e in manifest_entries if e['type'] == 'user_pdf' and e.get('readable'))
    print(f"arXiv papers: {arxiv_ok}/{arxiv_total} readable")
    print(f"User PDFs: {user_ok}/{len(user_results)} readable")

    return manifest['total_sources'], manifest['readable_count']


if __name__ == "__main__":
    total, readable = main()
    sys.exit(0 if readable >= 25 else 1)
