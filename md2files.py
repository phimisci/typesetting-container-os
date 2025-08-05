'''
This script converts Markdown files to various output formats using Pandoc.
Currently supported output formats are: PDF, HTML, LaTeX, and JATS.
The container expects a yaml file with metadata and a markdown file
Optionally, a BibTeX bibliography and individual Lua filters can be passed.
'''

import argparse
import os
import subprocess
import shutil

def parse_arguments():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser(
        description="Convert Markdown file to multiple output files using " \
                    "Pandoc (PDF, HTML, XML and more)."
                    )
    parser.add_argument(
        "markdown_file", 
        type=str, 
        help="The markdown file. This file should be in Markdown format and " \
             "stored in the subfolder 'article/'."
        )
    parser.add_argument(
        "metadata_file", 
        type=str, 
        help="The metadata file to use. This file should be in YAML format and" \
        " it should be produced by XML2YAML based on an OJS article metadata file."
        )
    parser.add_argument(
        "--bibtex", 
        dest="bibtex_file", 
        type=str, 
        help="The BibTeX file. This file should be in BibTeX format and stored" \
             " in the subfolder 'article/'. The file must have a .bib extension!"
        )
    parser.add_argument(
        "--filter", 
        "-f", 
        nargs="+", 
        default=[],
        help="Pandoc Lua-filters to use. These filters must be stored in the" \
        " subfolder 'filter/'. Please provide the filter name WITH the " \
        "file extension."
        )
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML file based on the template 'MMM_HTML_TEMPLATE.html'" \
             " in the subfolder called 'templates/'."
        )
    parser.add_argument(
        "--jats", 
        action="store_true", 
        help="Generate JATS file."
        )
    parser.add_argument(
        "--tex", 
        action="store_true", 
        help="Generate LaTeX file."
        )
    parser.add_argument(
        "--pdf", 
        action="store_true", 
        help="Generate PDF file based on a template from the subfolder" \
        " 'templates/'."
        )
    parser.add_argument(
        "--proof", 
        action="store_true", 
        help="Generate proof PDF file based on a template from the " \
        "subfolder 'templates/'."
        )
    parser.add_argument(
        "--filename", 
        type=str, 
        help="The name of the output file. This is an optional argument. " \
        "If not provided, the name of the markdown file will be used."
        )
    parser.add_argument(
        "--layout",
        type=str,
        help="The layout in use"
    )
    parser.add_argument(
        "--compounds",
        action="store_true",
        help="Whether to apply the filter for better hyphenation in compounds."
    )
    parser.add_argument(
        "--parentheses",
        action="store_true",
        help="Whether a citation style with manual parentheses is to be used."
    )
    parser.add_argument(
        "--widows",
        action="store_true",
        help="Automatically treat widows."
    )
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
    """
    Copy image files to from /app/article to /app working directory. 
    Necessary for image processing using Docker.
    """
    for filename in os.listdir("article/"):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            shutil.copy2(f"article/{filename}", "/app")

def construct_pandoc(
        *,
        standalone=True,
        lua_filters=[],
        bibliography_processing="citeproc",
        bibliography_csl_style=None,
        bibliography_manual_parentheses=False,
        bibliography_file=None,
        number_sections=True,
        pdf_engine=None,
        pdf_engine_options = {
            "latexmk": ["-lualatex", "-diagnostics"]
        },
        html_options = [],
        from_format="markdown",
        template=None,
        proofs=False,
        automatic_widow_removal=False,
        input_metadata=None,
        input_file=None,
        input_journal_metadata=None,
        input_bibliography_metadata_file=False,
        output_format=None,
        output_file=None,
        ):
    """
    Build options for the command based on user options.
    """
    a = ["pandoc"]
    if standalone:
        a.append("-s")

    try:
        for f in lua_filters:
            a.append(f"--lua-filter=filter/{f}")
    except TypeError:
        pass
    
    if bibliography_processing == "citeproc":
        a.append("--citeproc")
        if bibliography_csl_style:
            a.append("--csl")
            a.append(bibliography_csl_style)
        else:
            raise ValueError("No CSL specified.")
        
    if bibliography_processing == "biblatex":
        a.append("--biblatex")
        if bibliography_manual_parentheses:
            a.append("-M")
            a.append("parentheses")

    if number_sections:
        a.append("--number-sections")

    if from_format:
        a.append("--from")
        a.append(from_format)
    else:
        raise ValueError("No source format specified.")
    
    if template:
        a.append("--template")
        a.append(template)
    else:
        raise ValueError("No template specified.")
    
    if bibliography_file:
        a.append("--bibliography")
        a.append(bibliography_file)

    if pdf_engine:
        a.append("--pdf-engine")
        a.append(pdf_engine)

        try:
            # If there are options for a PDF engine, apply them.
            for o in pdf_engine_options[pdf_engine]:
                a.append(f"--pdf-engine-opt={o}")
        except KeyError:
            # Not all PDF engines need to have options.
            pass

    for o in html_options:
        a.append(o)

    if proofs:
        a.append("-M")
        a.append("proofs")

    if automatic_widow_removal:
        a.append("-M")
        a.append("widows")

    if input_journal_metadata:
        a.append(input_journal_metadata)

    if input_metadata:
        a.append(input_metadata)
    
    if input_file:
        a.append(input_file)
    else:
        raise ValueError("Input file not specified.")
    
    if input_bibliography_metadata_file and bibliography_file:
        a.append("tex/bibliography-preamble.tex")
    
    if output_format:
        a.append("-t")
        a.append(output_format)

    if output_file:
        a.append("-o")
        a.append(output_file)
    else:
        raise ValueError("Not output file specified.")
    
    return subprocess.run(a, capture_output=True, text=True)



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

    if args.filename:
        PLAINFILENAME = os.path.join("article/", args.filename)  
    else: 
        PLAINFILENAME = os.path.splitext(INMARKDOWN)[0]
    LOGFILE = f"article/PROCESS.log"

    # Set output filenames
    PDFFILE = f"{PLAINFILENAME}.pdf"
    PROOFFILE = f"{PLAINFILENAME}-PROOF.pdf"
    HTMLFILE = f"{PLAINFILENAME}.html"
    TEXFILE = f"{PLAINFILENAME}.tex"
    JATSFILE = f"{PLAINFILENAME}.jats"
    BIBLIOGRAPHY = f"{INBIBTEX}" if INBIBTEX else None
    active_filters = [i for i in args.filter]
    if args.compounds:
        active_filters.append("latex-compound-words.lua")

    if args.parentheses:
        CSLFILE = "csl/apa7-manual-parentheses.csl"
        PARENTHESES = True
    else:
        CSLFILE = "csl/apa7-single-spaced.csl"
        PARENTHESES = False

    if args.layout == "classic":
        TEXTEMPLATE = "templates/phimisci-classic.tex"
    if args.layout == "twocolumn":
        TEXTEMPLATE = "templates/phimisci-twocolumn.tex"

    copy_files_to_app_dir()

    if args.layout == "classic":
        base_config = {
            "lua_filters": active_filters,
            "bibliography_processing": "citeproc",
            "bibliography_csl_style": CSLFILE,
            "pdf_engine": "xelatex",
            "bibliography_file": BIBLIOGRAPHY,
            "template": TEXTEMPLATE,
            "input_journal_metadata": "templates/MMM_JOURNAL_METADATA.yaml",
            "input_metadata": INMETADATA,
            "input_file": INMARKDOWN,
            "input_bibliography_metadata_file": True,
        }
    
    if args.layout=="twocolumn":
        base_config = {
            "lua_filters": active_filters,
            "bibliography_processing": "biblatex",
            "bibliography_manual_parentheses": PARENTHESES,
            "pdf_engine": "latexmk",
            "bibliography_file": BIBLIOGRAPHY,
            "template": TEXTEMPLATE,
            "input_metadata": INMETADATA,
            "input_file": INMARKDOWN,
            "automatic_widow_removal": args.widows
        }

    # PUBLICATION PDF
    if args.pdf:
        result = construct_pandoc(
            **base_config, 
            output_file=PDFFILE
            )
        logging(LOGFILE, result)

    # PROOFS
    if args.proof:
        result = construct_pandoc(
            **base_config,
            proofs=True,
            output_file=PROOFFILE
            )
        logging(LOGFILE, result)

    # TEX SOURCE FILE
    if args.tex:
        result = construct_pandoc(
            **base_config,
            output_file=TEXFILE
            )
        logging(LOGFILE, result)


    # JATS generation
    if args.jats:
        result = construct_pandoc(
            lua_filters=active_filters,
            bibliography_processing="citeproc",
            bibliography_file=BIBLIOGRAPHY,
            input_journal_metadata="templates/MMM_JOURNAL_METADATA.yaml",                    
            input_metadata=INMETADATA,
            input_file=INMARKDOWN,
            output_format="jats+element_citations",
            output_file=JATSFILE
        )
        logging(LOGFILE, result)


    # HTML generation
    if args.html:
        result = construct_pandoc(
            lua_filters=active_filters,
            bibliography_processing="citeproc",
            html_options=["--mathjax"],
            template="templates/MMM_HTML_TEMPLATE.html",
            bibliography_file=BIBLIOGRAPHY,
            bibliography_csl_style=CSLFILE,
            input_journal_metadata="templates/MMM_JOURNAL_METADATA.yaml",
            input_metadata=INMETADATA,
            input_file=INMARKDOWN,
            output_file=HTMLFILE
        )
        logging(LOGFILE, result)

    print("Conversion finished.")

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
