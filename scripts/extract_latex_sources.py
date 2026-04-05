#!/usr/bin/env python3
"""
Phase 2: LaTeX Source Extraction Script
Extracts content from arXiv LaTeX sources into normalized content.md files.
"""

import os
import re
import sys
from pathlib import Path
import yaml


def find_main_tex_file(source_dir):
    """Find the main .tex file (the one with \\begin{document})."""
    tex_files = list(Path(source_dir).glob("*.tex"))
    
    for tex_file in tex_files:
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if r'\begin{document}' in content:
                    return tex_file
        except Exception:
            continue
    
    # Fallback: return the largest .tex file
    if tex_files:
        return max(tex_files, key=lambda f: f.stat().st_size)
    
    return None


def strip_latex_comments(text):
    """Remove LaTeX comments."""
    lines = []
    for line in text.split('\n'):
        # Remove comments but preserve escaped %
        line = re.sub(r'(?<!\\)%.*$', '', line)
        lines.append(line)
    return '\n'.join(lines)


def extract_section(text, section_name):
    """Extract a section from LaTeX text."""
    # Try various section patterns
    patterns = [
        rf'\\section\{{\s*{section_name}\s*\}}(.*?)(?=\\section\{{|\\end\{{document\}}|$)',
        rf'\\section\*\{{\s*{section_name}\s*\}}(.*?)(?=\\section|\\end\{{document\}}|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_abstract(text):
    """Extract abstract from LaTeX text."""
    # Try various abstract patterns
    patterns = [
        r'\\begin\{abstract\}(.*?)\\end\{abstract\}',
        r'\\abstract\{(.*?)\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return None


def clean_latex_text(text):
    """Clean LaTeX commands while preserving math and structure."""
    # Preserve displayed math
    text = re.sub(r'\\\[(.*?)\\\]', r'\n$$\1$$\n', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', r'\n$$\1$$\n', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', r'\n$$\1$$\n', text, flags=re.DOTALL)
    
    # Preserve inline math
    text = re.sub(r'\$\$(.*?)\$\$', lambda m: f'$${m.group(1)}$$', text)
    text = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', lambda m: f'${m.group(1)}$', text)
    
    # Remove common LaTeX commands
    text = re.sub(r'\\label\{[^}]*\}', '', text)
    text = re.sub(r'\\ref\{[^}]*\}', '[ref]', text)
    text = re.sub(r'\\cite\{[^}]*\}', '[citation]', text)
    text = re.sub(r'\\citep?\{[^}]*\}', '[citation]', text)
    text = re.sub(r'\\footnote\{[^}]*\}', '', text)
    
    # Remove figure/table environments
    text = re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', '', text, flags=re.DOTALL)
    
    # Common text formatting
    text = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'*\1*', text)
    text = re.sub(r'\\texttt\{([^}]*)\}', r'`\1`', text)
    
    # Remove itemize/enumerate environments but keep content
    text = re.sub(r'\\begin\{itemize\}', '', text)
    text = re.sub(r'\\end\{itemize\}', '', text)
    text = re.sub(r'\\begin\{enumerate\}', '', text)
    text = re.sub(r'\\end\{enumerate\}', '', text)
    text = re.sub(r'\\item\s+', '\n- ', text)
    
    # Remove other common commands
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def extract_latex_content(source_dir):
    """Extract content from LaTeX source to markdown."""
    main_tex = find_main_tex_file(source_dir)
    
    if not main_tex:
        return None, "No .tex file found"
    
    try:
        with open(main_tex, 'r', encoding='utf-8', errors='ignore') as f:
            full_text = f.read()
    except Exception as e:
        return None, f"Failed to read {main_tex}: {e}"
    
    # Strip comments first
    full_text = strip_latex_comments(full_text)
    
    # Extract sections
    sections = {}
    
    # Abstract
    abstract = extract_abstract(full_text)
    if abstract:
        sections['Abstract'] = clean_latex_text(abstract)
    
    # Main sections
    section_names = ['Introduction', 'Related Work', 'Methodology', 'Methods', 
                     'Approach', 'Results', 'Experiments', 'Analysis', 
                     'Discussion', 'Conclusion', 'Conclusions']
    
    for section_name in section_names:
        content = extract_section(full_text, section_name)
        if content:
            sections[section_name] = clean_latex_text(content)
    
    if not sections:
        # Fallback: extract everything between \begin{document} and \end{document}
        doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', full_text, re.DOTALL)
        if doc_match:
            content = clean_latex_text(doc_match.group(1))
            if len(content) > 500:
                return content, None
        
        return None, "Could not extract meaningful content"
    
    # Build markdown
    markdown_parts = []
    
    for section_title, section_content in sections.items():
        if section_content:
            markdown_parts.append(f"## {section_title}\n\n{section_content}\n")
    
    markdown = '\n'.join(markdown_parts)
    
    if len(markdown) < 500:
        return None, f"Extracted content too short ({len(markdown)} chars)"
    
    return markdown, None


def verify_content_file(content_path):
    """Verify a content file exists and is readable."""
    if not os.path.exists(content_path):
        return False, "File does not exist"
    
    try:
        with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if len(content) < 500:
                return False, f"Content too short ({len(content)} chars)"
            return True, len(content)
    except Exception as e:
        return False, f"Failed to read: {e}"


def main():
    """Main extraction workflow."""
    workspace_root = Path(__file__).parent.parent
    manifest_path = workspace_root / "sources" / "manifest.yaml"
    
    print(f"Reading manifest: {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        manifest = yaml.safe_load(f)
    
    sources = manifest.get('sources', [])
    print(f"Found {len(sources)} sources in manifest\n")
    
    stats = {
        'total': len(sources),
        'extracted': 0,
        'verified': 0,
        'failed': 0,
        'skipped': 0
    }
    
    failed_sources = []
    
    for source in sources:
        source_id = source['id']
        source_type = source['type']
        local_path = workspace_root / source['local_path']
        
        print(f"Processing {source_id} ({source_type})...")
        
        # Determine content file path
        if source_type == 'arxiv':
            content_path = local_path / 'content.md'
            
            # Check if already extracted
            if content_path.exists():
                is_valid, result = verify_content_file(content_path)
                if is_valid:
                    print(f"  ✓ Already extracted ({result} chars)")
                    stats['verified'] += 1
                    source['extracted'] = True
                    source['content_file'] = f"sources/{source_id}/content.md"
                    source['char_count'] = result
                    continue
            
            # Extract from LaTeX
            print(f"  Extracting from LaTeX...")
            markdown, error = extract_latex_content(local_path)
            
            if error:
                print(f"  ✗ Failed: {error}")
                stats['failed'] += 1
                failed_sources.append((source_id, error))
                source['extracted'] = False
                source['extraction_error'] = error
                continue
            
            # Write content.md
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"  ✓ Extracted ({len(markdown)} chars)")
            stats['extracted'] += 1
            source['extracted'] = True
            source['content_file'] = f"sources/{source_id}/content.md"
            source['char_count'] = len(markdown)
        
        elif source_type in ['user-pdf', 'blog', 'tutorial']:
            # Verify existing content file
            content_file_rel = source.get('content_file', '')
            
            if not content_file_rel:
                print(f"  ✗ No content_file specified")
                stats['failed'] += 1
                failed_sources.append((source_id, "No content_file in manifest"))
                source['extracted'] = False
                continue
            
            content_path = workspace_root / content_file_rel
            is_valid, result = verify_content_file(content_path)
            
            if is_valid:
                print(f"  ✓ Verified ({result} chars)")
                stats['verified'] += 1
                source['extracted'] = True
                source['char_count'] = result
            else:
                print(f"  ✗ Verification failed: {result}")
                stats['failed'] += 1
                failed_sources.append((source_id, result))
                source['extracted'] = False
    
    # Write updated manifest
    print(f"\nUpdating manifest...")
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total sources:      {stats['total']}")
    print(f"Newly extracted:    {stats['extracted']}")
    print(f"Already verified:   {stats['verified']}")
    print(f"Failed:             {stats['failed']}")
    print(f"Success rate:       {(stats['extracted'] + stats['verified']) / stats['total'] * 100:.1f}%")
    
    if failed_sources:
        print(f"\nFailed sources:")
        for source_id, error in failed_sources:
            print(f"  - {source_id}: {error}")
    
    return 0 if stats['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
