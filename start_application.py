'''
Script to start the application. Called by the Dockerfile via ENTRYPOINT. Web interface is started if argument --webinterface is passed. In this case, you need to run the Docker container with the -p 5000:5000 option to access the webinterface. If any other arguments besides --webinterace are passed, the script md2files.py is run with these arguments. In this case, you need to mount the article folder you are currently in via -v $(pwd):/app/article
'''

# Version: 1.0.0
# Date: 2024-10-04
# by Thomas Jurczyk (c) MIT License (see LICENSE file)

import subprocess, argparse, sys

def parse_arguments() -> argparse.Namespace:
    '''Parse command line arguments.
    
        Returns
        -------
        argparse.Namespace
            The command line arguments.
    
    '''
    parser = argparse.ArgumentParser(description="Start Typesetting Container: Either Webinterface or directly start processing.")
    # Only arg for the webinterface
    parser.add_argument("--webinterface", action="store_true", help="Start the webinterface.")
    # All other args are for manual start of the typesetting container
    parser.add_argument("--markdown_file", type=str, help="The markdown file. This file should be in Markdown format and stored in the subfolder 'article/'.")
    parser.add_argument("--metadata_file", type=str, help="The metadata file to use. This file should be in YAML format and it should be procuded by XML2YAML based on an OJS article metadata file.")
    parser.add_argument("--bibtex_file", type=str, help="The BibTeX file. This file should be in BibTeX format and stored in the subfolder 'article/'. The file must have a .bib extension!")
    parser.add_argument("--filter", "-f", nargs="+", help="Pandoc Lua-filters to use. These filters must be stored in the subfolder 'filter/'. Please provide the filter name WITH the file extension.")
    parser.add_argument("--html", action="store_true", help="Generate HTML file based on the template 'MMM_HTML_TEMPLATE.tex' in the subfolder called 'templates/'.")
    parser.add_argument("--jats", action="store_true", help="Generate JATS file.")
    parser.add_argument("--tex", action="store_true", help="Generate LaTeX file.")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF file based on the template 'MMM_PDF_TEMPLATE.tex' in the subfolder called 'templates/'.")
    parser.add_argument("--filename", type=str, help="The name of the output file. This is an optional argument. If not provided, the name of the markdown file will be used.")
    return parser.parse_args()

def main(args) -> None:
    '''Main function to start the application.
    
        Parameters
        ----------
        args : argparse.Namespace
            The command line arguments

        Returns
        -------
        None
    
    '''
    if args.webinterface:
        from webinterface.app import app
        # Note that the webinterface is run in debug mode by default!
        # This is not recommended for production use!
        app.run(host="0.0.0.0",port=5000, debug=True)
    else: # Start the typesetting container
        # Create command
        command = ['python3', 'md2files.py']
        if args.markdown_file:
            command.append(args.markdown_file)
        if args.metadata_file:
            command.append(args.metadata_file)
        if args.bibtex_file:
            command.append("--bibtex")
            command.append(args.bibtex_file)
        if args.filter:
            command.append("--filter")
            command.extend(args.filter)
        if args.html:
            command.append("--html")
        if args.pdf:
            command.append("--pdf")
        if args.jats:
            command.append("--jats")
        if args.tex:
            command.append("--tex")
        if args.filename:
            command.append("--filename")
            command.append(args.filename)
        
        # Start the typesetting container
        subprocess.run(command, check=True)

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    # Start the webinterface
    main(args)
