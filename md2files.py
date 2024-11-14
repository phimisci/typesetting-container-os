'''
This script converts Markdown files to various output formats using Pandoc.
Currently supported output formats are: PDF, HTML, LaTeX, and JATS.
The container expects a yaml file with metadata and a markdown file
Optionally, a BibTeX bibliography and individual Lua filters can be passed.
'''

# Version: 1.0.0
# Date: 2024-10-04
# by Thomas Jurczyk (c)

import argparse, os, subprocess, shutil

def parse_arguments():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser(description="Convert Markdown file to multiple output files using Pandoc (PDF, HTML, XML and more).")
    parser.add_argument("markdown_file", type=str, help="The markdown file. This file should be in Markdown format and stored in the subfolder 'article/'.")
    parser.add_argument("metadata_file", type=str, help="The metadata file to use. This file should be in YAML format and it should be produced by XML2YAML based on an OJS article metadata file.")
    parser.add_argument("--bibtex", dest="bibtex_file", type=str, help="The BibTeX file. This file should be in BibTeX format and stored in the subfolder 'article/'. The file must have a .bib extension!")
    parser.add_argument("--filter", "-f", nargs="+", help="Pandoc Lua-filters to use. These filters must be stored in the subfolder 'filter/'. Please provide the filter name WITH the file extension.")
    parser.add_argument("--html", action="store_true", help="Generate HTML file based on the template 'MMM_HTML_TEMPLATE.html' in the subfolder called 'templates/'.")
    parser.add_argument("--jats", action="store_true", help="Generate JATS file.")
    parser.add_argument("--tex", action="store_true", help="Generate LaTeX file.")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF file based on the template 'MMM_PDF_TEMPLATE.tex' in the subfolder called 'templates/'.")
    parser.add_argument("--filename", type=str, help="The name of the output file. This is an optional argument. If not provided, the name of the markdown file will be used.")
    return parser.parse_args()

def logging(LOGFILE: str, result: subprocess.CompletedProcess) -> None:
    """Write the stdout and stderr of a command execution to a log file.
    
        Parameters
        ----------
        LOGFILE : str
            The name of the log file.
        result : subprocess.CompletedProcess
            The result of the command execution.

        Returns
        -------
        None

    """
    with open(LOGFILE, "a") as f:
        f.write(result.stdout)
        f.write(result.stderr)

def copy_files_to_app_dir() -> None:
    """Copy image files to from /app/article to /app working directory. Necessary for image processing using Docker."""
    for filename in os.listdir("article/"):
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            shutil.copy2(f"article/{filename}", "/app")

def main(args) -> None:
    '''Main function to convert the markdown file to various output formats.

        Parameters
        ----------
        args : argparse.Namespace
            The command line arguments.

        Returns
        -------
        None
    
    '''
    INMARKDOWN = f"article/{args.markdown_file}"
    INMETADATA = f"article/{args.metadata_file}"
    INBIBTEX = f"article/{args.bibtex_file}" if args.bibtex_file else None

    PLAINFILENAME = os.path.join("article/", args.filename) if args.filename else os.path.splitext(INMARKDOWN)[0]
    LOGFILE = f"article/PROCESS.log"

    # Set output filenames
    PDFFILE = f"{PLAINFILENAME}.pdf"
    HTMLFILE = f"{PLAINFILENAME}.html"
    TEXFILE = f"{PLAINFILENAME}.tex"
    JATSFILE = f"{PLAINFILENAME}.jats"
    BIBLIOGRAPHY = f"{INBIBTEX}" if INBIBTEX else None

    copy_files_to_app_dir()

    # PDF generation
    if args.pdf:
        PDF_BASE_COMMAND = [
            "pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown",
            "--template=templates/MMM_PDF_TEMPLATE.tex", "--bibliography", BIBLIOGRAPHY, "--csl=csl/MMM_CSL.csl",
            "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", PDFFILE
        ] if BIBLIOGRAPHY else [
            "pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown",
            "--template=templates/MMM_PDF_TEMPLATE.tex", "--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml",
            INMETADATA, INMARKDOWN, "-o", PDFFILE
        ]
        if args.filter:
            for filter in reversed(args.filter):
                PDF_BASE_COMMAND.insert(2, f"--lua-filter=filter/{filter}")
        result = subprocess.run(PDF_BASE_COMMAND, capture_output=True, text=True)
        logging(LOGFILE, result)

    # LaTeX generation
    if args.tex:
        TEX_COMMAND = [
            "pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown",
            "--template=templates/MMM_PDF_TEMPLATE.tex", "--bibliography", BIBLIOGRAPHY, "--csl=csl/MMM_CSL.csl",
            "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", TEXFILE
        ] if BIBLIOGRAPHY else [
            "pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown",
            "--template=templates/MMM_PDF_TEMPLATE.tex", "--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml",
            INMETADATA, INMARKDOWN, "-o", TEXFILE
        ]
        if args.filter:
            for filter in reversed(args.filter):
                TEX_COMMAND.insert(1, f"--lua-filter=filter/{filter}")
        result = subprocess.run(TEX_COMMAND, capture_output=True, text=True)
        logging(LOGFILE, result)

    # JATS generation
    if args.jats:
        JATS_COMMAND = [
            "pandoc", "--citeproc", "--number-sections", "-s", "-N", "--from", "markdown",
            "--bibliography", BIBLIOGRAPHY, "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN,
            "-t", "jats+element_citations", "-o", JATSFILE
        ] if BIBLIOGRAPHY else [
            "pandoc", "--citeproc", "--number-sections", "-s", "-N", "--from", "markdown",
            "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-t", "jats+element_citations", "-o", JATSFILE
        ]
        if args.filter:
            for filter in reversed(args.filter):
                JATS_COMMAND.insert(1, f"--lua-filter=filter/{filter}")
        result = subprocess.run(JATS_COMMAND, capture_output=True, text=True)
        logging(LOGFILE, result)

    # HTML generation
    if args.html:
        HTML_COMMAND = [
            "pandoc", "--citeproc", "--number-sections", "--mathjax", "--from", "markdown",
            "--template=templates/MMM_HTML_TEMPLATE.html", "--bibliography", BIBLIOGRAPHY, "--csl=csl/MMM_CSL.csl",
            "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", HTMLFILE
        ] if BIBLIOGRAPHY else [
            "pandoc", "--citeproc", "--number-sections", "--mathjax", "--from", "markdown",
            "--template=templates/MMM_HTML_TEMPLATE.html", "--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml",
            INMETADATA, INMARKDOWN, "-o", HTMLFILE
        ]
        if args.filter:
            for filter in reversed(args.filter):
                HTML_COMMAND.insert(1, f"--lua-filter=filter/{filter}")
        result = subprocess.run(HTML_COMMAND, capture_output=True, text=True)
        logging(LOGFILE, result)

    print("Conversion finished.")

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
