# Magic Manuscript Maker – Typesetting Container OS

## Introduction
This repository contains the code for the typesetting container of the journal "Philosophy and the Mind Sciences" (PhiMiSci). The typesetting container can be used to convert journal articles submitted in Markdown, which can be processed with Pandoc, into various formats. The container is currently configured to output the following formats:

1. PDF
2. HTML
3. JATS
4. TEX

The typesetting container was originally developed for the workflow of the journal "Philosophy and the Mind Sciences." The version provided here is an extension of this workflow and can also be used by other journals.

The container is configured to be run via Docker. It can be operated either through the command line interface or started as a web application. The typesetting container can be used directly with the supplied standard templates without any further configuration. However, you can also adjust or replace the standard templates with custom templates.

## Requirements
### Pandoc
The typesetting workflow is designed to process Markdown files with [Pandoc](https://pandoc.org) and convert them into the four mentioned output formats. Pandoc is a universal document converter that is open-source and was developed by John MacFarlane. The typesetting workflow accepts the Markdown flavor supported by Pandoc version 3.4, including citations in the Citeproc format. Additionally, Lua filters can be used to influence the conversion, with only one filter for image referencing being provided by default.

### Docker
Docker is a container management system that allows applications to be isolated and executed in containers. Docker containers can be run on any system where Docker is installed, regardless of the environment. The typesetting container is provided as a Docker image, which includes all the necessary components to perform file conversions. The container can be run on any system with Docker installed and offers a simple way to use the typesetting workflow without needing to install Pandoc and LaTeX locally.

To install the Docker engine on your system, follow the instructions on the [Docker website](https://docs.docker.com/get-docker/).

## Installation
Once the Docker engine is installed, there are two ways to create the container image: either by building the image from the Dockerfile or by pulling the image from GitHub Container Registry.

### Pulling the image from GitHub container registry

The typesetting container image can be pulled from the GitHub Container Registry. To do this, open a shell and run the following command:

`docker pull ghcr.io/phimisci/typesetting-container-os:latest`

### Local build of the Docker image
You can also build the Docker image locally from the Dockerfile provided in the repository. To do so, clone the repository to your local machine. Afterwards, open a shell in the root directory of the repository and run the following command (here on Linux):

`docker build -t typesetting-container .`

The tag `typesetting-container` can be chosen arbitrarily. It is used to reference the image more easily later. The build process may take some time, as the image is created based on `pandoc/latex` and requires the installation of additional packages.

## Web interface

To run the container using the web interface, use the following command:

`docker run -p 5000:5000 typesetting-container --webinterface`

We assume that the container is named `typesetting-container`. If you are using the image from the GitHub Container Registry, the image name is `ghcr.io/phimisci/typesetting-container-os:latest`. The `-p 5000:5000` flag maps port 5000 of the container to port 5000 of the host system.

A local web server with a Flask application will then be started, which can be accessed through a browser or by typing `http://localhost:5000` in the address bar of your browser. The web interface simplifies working with the typesetting workflow. The files can be downloaded directly after conversion.

However, running the previous command, the created files are are only temporarily saved in the container. After closing the container, the files are no longer available. If the files are to be stored permanently, a volume must be mounted. To store all files in the current directory, the following command can be used:

`docker run -p 5000:5000 --volume "$(pwd):/app/article" typesetting-container --webinterface`

### Required files
To convert an article using the typesetting workflow, at least the Markdown file must be uploaded. Additionally, a BibTeX file and image files can also be uploaded. The metadata of the article can either be entered directly in the web interface or uploaded via a YAML file.

Once all the information is ready, the desired output formats can be selected, and the conversion can be started. After the process is complete, the files will automatically be downloaded as a ZIP file. The ZIP file also contains a log file that includes any error messages or warnings that may have occurred during the conversion.

If the standard template is used, the metadata in YAML format must contain the following fields:

```yaml
---
title: 'The Eternal Boy: A Study in Agelessness and Memory'
subtitle: Exploring Identity, Temporality, and the Philosophy of Neverland
author:
- name: Wendy Darling
  affiliation:
  - organization: University of Oxford
  email: w.darling@oxford.ac.uk
  orcid: 0000-0002-5678-9012
- name: Peter Pan
  affiliation:
  - organization: SOAS London
  - organization: Neverland
  email: peter.pan@neverland.com
  orcid: 0000-1101-1234-5678
keywords:
- Agelessness
- Memory theory
- Identity
- Temporality
- Neverland metaphysics
- Fantasy ontology
- Child psychology
- Flight dynamics
abstract: |-
  How does the notion of agelessness shape identity and memory in an eternal youth like Peter Pan? This article examines the metaphysics of agelessness through the lens of Peter Pan’s unchanging form and his shifting memories, drawing from theories of temporality and identity. We argue that Neverland serves as a temporal vacuum, where time functions differently, creating unique challenges to traditional philosophical concepts of identity and selfhood. The implications of living outside of time, where one remains physically unchanged but psychologically impacted by infinite experiences, are explored. This work also touches on the phenomenology of flight, a central theme in Peter Pan’s existence, as it symbolizes his defiance of physical and temporal limitations. The article situates these discussions within the broader debate on fantasy ontology and its relation to real-world psychological and philosophical frameworks.
date: '2024'
volume: 7
doi: 10.1111/12345678
author-short: Darling & Pan
...

```

Don't forget to create a YAML block in the YAML file by using the three dashes `---` at the beginning and `...` at the end of the metadata block.

### Journal metadata
If you want to change the metadata of the journal, you can either do so directly in the web or by setting up a container with a custom metadata file for your journal. To customize the typesetting workflow container, please refer to the section "Customizing the Container."

## CLI usage of the Docker container
After the image has been created, the container can be used. First, a shell must be opened in the directory where the article files are located (Markdown, Metadata, BibTeX (optional), and images). In the directory, the following command can now be executed in the command line to create a PDF file from the source files:

`docker run --rm --volume "$(pwd):/app/article" mmm-typesetting-container --markdown_file Wirtz_2024.md --metadata_file metadata.yaml --bibtex_file Wirtz_2024.bib --pdf`

Using  Windows (PowerShell), the command is as follows:

`docker run --rm --volume "${PWD}:/app/article" mmm-typesetting-container --markdown_file Wirtz_2024.md --metadata_file metadata.yaml --bibtex_file Wirtz_2024.bib --pdf`

If an HTML version of the article should also be created, a corresponding flag can simply be added:

`docker run --rm --volume "${PWD}:/app/article" mmm-typesetting-container --markdown_file Wirtz_2024.md --metadata_file metadata.yaml --bibtex_file Wirtz_2024.bib --pdf --html`

Now both the PDF and the HTML are created. After the command is executed, a PDF file named `Wirtz_2024.pdf` and an HTML file named `Wirtz_2024.html` should be created in the directory. The filenames may vary depending on the container configuration. Additionally, a file named `PROCESS.log` is created, which contains any error messages or warnings (for example, if there is a Markdown syntax error that leads to a failed conversion). You can optionally also pass a filename for the output files using the `--filename` flag.

### Using Lua filters (optional)
The typesetting container also supports the use of [Lua filters](https://pandoc.org/lua-filters.html) for Pandoc to influence the conversion of the files. The filters can be added when calling the container via `--lua-filter`. In the vanilla version of the typesetting container, there is the option to call the `pandoc-figref.lua` filter, which allows referencing images and tables in Markdown. More information about this filter can be found [here](). A call to create a PDF using the `pandoc-figref.lua` filter is as follows (Linux):

`docker run --rm --volume "$(pwd):/app/article" mmm-typesetting-container --markdown_file Wirtz_2024.md --metadata_file metadata.yaml --bibtex_file Wirtz_2024.bib --pdf --lua-filter pandoc-figref.lua`

#### Linking images with pandoc-figref
If an image is to be linked within the text, a corresponding identifier must first be added to the image (see the following example):

```
![This is a caption.](figure1.png){#fig:figure1}
```

Now the image can be easily referenced in the text using the reference `fig:figure1` by prefixing it with an `@`:

```
See also figure @fig:figure1.
```

Currently, references are only supported in the output formats PDF, TEX, and HTML.

## Customizing the container
To customize the container, for example for a different journal, all files in the `templates`, `filter`, `csl`, and `fonts` folders can be replaced.

### Customizing the templates
The templates for the various output formats (PDF, HTML, JATS, TEX) are located in the `templates` folder. The templates are written in LaTeX or HTML and contain special variables that are replaced by Pandoc and taken from the metadata (YAML) file. Accordingly, the templates and the YAML metadata file must be closely coordinated. The templates can be customized as desired to change the appearance of the output, adhering to the specifications of Pandoc, see [Pandoc Documentation](https://pandoc.org/MANUAL.html#templates). The templates for the various output formats are found in the `templates` folder. It is important to ensure that the files are named according to the scheme `MMM_PDF_TEMPLATE.html` and saved in the `templates` folder. Additionally, the values of variables used in the template can be adjusted in the YAML file `MMM_JOURNAL_METADATA.yaml` to influence the output. This file also contains additional information used by Pandoc to format the output. These options can also be adjusted as needed.

After replacing the templates, the Docker image must be rebuilt to apply the changes and use the new templates.

Pandoc templates are quite complex but offer a very high degree of individual customization. For starters, it can be helpful to use an existing and freely available template of a journal and adapt it to your own needs.

There is one important caveat when changing the templates and the metadata structure in particular: Even though it is not a problem to upload the new metadata files in the web interface and create output files based on the new templates, the manual input of metadata in the web interface will most likely not work with a changed metadata structure. If you want to allow manual input of new metadata, you must adjust the web interface accordingly.

### Customizing the CSL file
Just like with the templates, the CSL file in the `csl` folder can be customized to adopt the citation style of the journal. The CSL file must be in CSL format and can be edited with any editor. The CSL file must be placed in the `csl` folder and named as follows: `MMM_CSL.csl`. The CSL file can be used after rebuilding the Docker image.

### Customizing the filters
Additional Lua filters can be easily stored in the `filter` folder and then passed as a list when calling the container in the CLI. The filters can be named arbitrarily but must be in Lua format and end with a `.lua` extension. The filters can be used to influence the conversion of the files, for example, to apply special formatting or adjustments.

Here is an example call to use the filters `my-filter.lua` and `my-filter-2.lua`:

`docker run --rm --volume "$(pwd):/app/article" mmm-typesetting-container --markdown_file Wirtz_2024.md --metadata_file metadata.yaml --bibtex_file Wirtz_2024.bib --pdf --lua-filter my-filter.lua --lua-filter my-filter-2.lua`

It is important to note that the order of the filter calls matters, as the filters are called sequentially and the output of the previous filter serves as the input for the next filter.

### Customizing the fonts
Adding fonts is a bit more complex and requires modifying the Dockerfile. The fonts must be in OpenType format and can be placed in the `fonts` folder. In the Dockerfile, the fonts must then be installed by adding the corresponding commands (see the relevant section in the Dockerfile). After adding the fonts and rebuilding the Docker image, the fonts can be used in the templates. By default, the [Linux Libertine](https://en.wikipedia.org/wiki/Linux_Libertine) and [OpenSans](https://fonts.google.com/specimen/Open+Sans) fonts are provided.

## Q&A

### Why should I use the typesetting container instead of just using Pandoc directly?
The typesetting container was primarily developed for editorial offices that use Markdown as the central format for their submissions and where it cannot be assumed that all editors have a deeper understanding of Pandoc. The container simplifies the conversion process by bundling the necessary steps in a Docker container and making them accessible via a simple command line or web interface, so that less technically savvy people can also use the typesetting workflow.

It also eliminates the need to install Pandoc and LaTeX locally, which can be a hurdle for many editors. The typesetting workflow is managed and versioned in one central place, while the editorial offices can work based on the current image. The container can also be easily operated on a server, further facilitating the centralization and handling of the workflow.

## Contributing
Contributions to the typesetting container are welcome. If you have any suggestions, improvements, or bug fixes, please feel free to open an issue or create a pull request. The typesetting container is intended to be a flexible and adaptable tool for various journals, and your contributions can help make it even better.

## About
This application was developed by Thomas Jurczyk (thomjur on GitHub) for the journal [Philosophy and the Mind Sciences](https://philosophymindscience.org/) as part of a project funded by the German Research Foundation (DFG).

## Versions
### 1.0.1 (10.04.2025)
- Bumping Pandoc to version 3.6.4.0

### 1.0.0 (31.10.2024)
- Initial release of the typesetting container
