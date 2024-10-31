# This script converts Markdown files to various output formats using Pandoc.
# Currently supportet output formats are: PDF, HTML, LaTeX, and JATS.
# The container expects a yaml file with metadata and a markdown file
# Optionally, a BibTeX bibligraphy and individual Lua filters can be passed.
# Version: 1.0.0
# Date: 2024-10-04
# by Thomas Jurczyk (c)

import argparse, os, subprocess, shutil

parser = argparse.ArgumentParser(description="Convert Markdown file to multiple output files using Pandoc (PDF, HTML, XML and more).")
parser.add_argument("markdown_file", type=str, help="The markdown file. This file should be in Markdown format and stored in the subfolder 'article/'.")
parser.add_argument("metadata_file", type=str, help="The metadata file to use. This file should be in YAML format and it should be procuded by XML2YAML based on an OJS article metadata file.")
parser.add_argument("--bibtex", dest="bibtex_file", type=str, help="The BibTeX file. This file should be in BibTeX format and stored in the subfolder 'article/'. The file must have a .bib extension!")
parser.add_argument("--filter", "-f", nargs="+", help="Pandoc Lua-filters to use. These filters must be stored in the subfolder 'filter/'. Please provide the filter name WITH the file extension.")
parser.add_argument("--html", action="store_true", help="Generate HTML file based on the template 'MMM_HTML_TEMPLATE.html' in the subfolder called 'templates/'.")
parser.add_argument("--jats", action="store_true", help="Generate JATS file.")
parser.add_argument("--tex", action="store_true", help="Generate LaTeX file.")
parser.add_argument("--pdf", action="store_true", help="Generate PDF file based on the template 'MMM_PDF_TEMPLATE.tex' in the subfolder called 'templates/'.")
parser.add_argument("--filename", type=str, help="The name of the output file. This is an optional argument. If not provided, the name of the markdown file will be used.")
args = parser.parse_args()

# Set input filenames with path
# This typesetting container expects a yaml file with metadata and a markdown file as input.
INMARKDOWN=f"article/{args.markdown_file}"
INMETADATA=f"article/{args.metadata_file}"
INBIBTEX=f"article/{args.bibtex_file}" if args.bibtex_file else None

# If file name is provided, use this name for the output files
if args.filename:
    PLAINFILENAME = os.path.join("article/", args.filename)
else: 
    # Get markdown file name without extension    
    PLAINFILENAME, _ = os.path.splitext(INMARKDOWN)

# Create log file 
LOGFILE=f"article/PROCESS.log"

def logging(LOGFILE: str, result: subprocess.CompletedProcess) -> None:
    """
    Write the stdout and stderr of a command execution to a log file.

        Parameters
        ----------
            LOGFILE (str):
                The path to the log file.
            result (subprocess.CompletedProcess):
                The result of the command execution.

        Returns
        -------
            None
    """
    with open(LOGFILE, "a") as f:
        f.write(result.stdout)
        f.write(result.stderr)

# Set output filenames
PDFFILE=f"{PLAINFILENAME}.pdf"
HTMLFILE=f"{PLAINFILENAME}.html"
TEXFILE=f"{PLAINFILENAME}.tex"
JATSFILE=f"{PLAINFILENAME}.jats"
BIBLIOGRAPHY=f"{INBIBTEX}" if INBIBTEX else None

# IMPORTANT for Docker: This part is necessary for the image processing. Pandoc is run in /app, however, the files are stored in /app/article (because of volume mounting). The markdown file usually refers to the images in the same folder. Therefore, we need to copy the files from /app/article to /app (the working directory of Pandoc in the Docker container).

def copy_files_to_app_dir() -> None:
    """Copy image files to from /app/article to /app working directory. Necessary for image processing using Docker."""
    for filename in os.listdir("article/"):
        # Make sure to only copy image files
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            shutil.copy2(f"article/{filename}", "/app")

# Copy image files to app directory
copy_files_to_app_dir()

# Render PDF using the template MMM_PDF_TEMPLATE.tex
if args.pdf:
    # Check if a bibliography file is provided
    if BIBLIOGRAPHY:
        PDF_BASE_COMMAND = ["pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown", f"--template=templates/MMM_PDF_TEMPLATE.tex", "--bibliography", BIBLIOGRAPHY, f"--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", PDFFILE]
    else:
        PDF_BASE_COMMAND = ["pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown", f"--template=templates/MMM_PDF_TEMPLATE.tex", f"--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", PDFFILE]
    # Check if filters are provided
    if args.filter:
        filter_list = args.filter
        filter_list.reverse()
        for filter in filter_list:
            PDF_BASE_COMMAND.insert(2, f"--lua-filter=filter/{filter}")

    # Start Pandoc
    result = subprocess.run(PDF_BASE_COMMAND, capture_output=True, text=True)

    # Add logging
    logging(LOGFILE, result)

# Create LaTeX file
if args.tex:
    if BIBLIOGRAPHY:
        TEX_COMMAND = ["pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown", f"--template=templates/MMM_PDF_TEMPLATE.tex", "--bibliography", BIBLIOGRAPHY, f"--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", TEXFILE]
    else:
        TEX_COMMAND = ["pandoc", "-s", "--citeproc", "--number-sections", "--pdf-engine=xelatex", "--from", "markdown", f"--template=templates/MMM_PDF_TEMPLATE.tex", f"--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", TEXFILE]   

    # Check if filters are provided
    if args.filter:
        filter_list = args.filter
        filter_list.reverse()
        for filter in filter_list:
            TEX_COMMAND.insert(1, f"--lua-filter=filter/{filter}")

    # Start Pandoc
    result = subprocess.run(TEX_COMMAND, capture_output=True, text=True)

    # Add logging
    logging(LOGFILE, result)

# Create JATS file
if args.jats:
    if BIBLIOGRAPHY:
        JATS_COMMAND = ["pandoc", "--citeproc", "--number-sections", "-s", "-N", "--from", "markdown", "--bibliography", BIBLIOGRAPHY, "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-t", "jats+element_citations", "-o", JATSFILE]
    else:
        JATS_COMMAND = ["pandoc", "--citeproc", "--number-sections", "-s", "-N", "--from", "markdown", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-t", "jats+element_citations", "-o", JATSFILE]

    # Check if filters are provided
    if args.filter:
        filter_list = args.filter
        filter_list.reverse()
        for filter in filter_list:
            JATS_COMMAND.insert(1, f"--lua-filter=filter/{filter}")

    # Start Pandoc
    result = subprocess.run(JATS_COMMAND, capture_output=True, text=True)

    # Add logging
    logging(LOGFILE, result)

# Create HTML file
if args.html:
    # Check if a bibliography file is provided
    if BIBLIOGRAPHY:
        HTML_COMMAND = ["pandoc", "--citeproc", "--number-sections", "--mathjax", "--from", "markdown", "--template=templates/MMM_HTML_TEMPLATE.html", "--bibliography", BIBLIOGRAPHY, "--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", HTMLFILE]
    else:
        HTML_COMMAND = ["pandoc", "--citeproc", "--number-sections", "--mathjax", "--from", "markdown", "--template=templates/MMM_HTML_TEMPLATE.html", "--csl=csl/MMM_CSL.csl", "templates/MMM_JOURNAL_METADATA.yaml", INMETADATA, INMARKDOWN, "-o", HTMLFILE]
    # Check if filters are provided
    if args.filter:
        filter_list = args.filter
        filter_list.reverse()
        for filter in filter_list:
            HTML_COMMAND.insert(1, f"--lua-filter=filter/{filter}")

    # Start Pandoc
    result = subprocess.run(HTML_COMMAND, capture_output=True, text=True)

    # Add logging
    logging(LOGFILE, result)

print("Conversion finished.")