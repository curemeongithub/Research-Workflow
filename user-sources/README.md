# user-sources/

Drop your own PDF files here before running the research pipeline.

The Phase 1 (source-acquisition) agent will automatically detect and process any PDFs in this directory using Mistral OCR, incorporating them into the research alongside the papers it downloads.

## Supported Formats

- `.pdf` — standard PDF files (papers, reports, textbook chapters)
- Handwritten PDFs are supported via `scripts/onenote_pdf_to_markdown.py`

## How It Works

1. Drop your PDFs here before starting the pipeline
2. Run: `"Research [topic] for me"`
3. Phase 1 will process your PDFs into `sources/user-{filename}/content.md`
4. They appear in `sources/manifest.yaml` with `type: user-pdf`
5. Phases 3-9 incorporate them like any other source

## Notes

- Files here are **not** automatically added to git (see `.gitignore`)
- Source extraction output lives in `sources/user-{filename}/` (which IS tracked)
