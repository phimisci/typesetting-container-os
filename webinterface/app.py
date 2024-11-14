'''
This module contains the Flask application for the web interface of the Typesetting Container OS tool.
'''

from flask import Flask, render_template, send_file, flash, redirect, url_for
import subprocess
import os
from .forms import UploadForm, JournalDataForm
from flask_wtf.csrf import CSRFProtect
from io import BytesIO
import zipfile
import yaml

app = Flask(__name__)

# Important: Change this secret key if you plan to use this in production!!!
# Ideally, this key should be stored in an environment variable
app.config['SECRET_KEY'] = 'PleaseChangeThisSecretKeyIfYouPlanToUseThisInProduction123124342424234!?!=!'

# Enable CSRF protection
csrf = CSRFProtect(app)

# Helper functions
def create_metadata_yaml_from_input(upload_form: UploadForm) -> None:
    '''Generates a metadata.yaml file from the provided upload form data.

        Parameters
        ----------
        upload_form : UploadForm
            An object containing the article's metadata input fields.

        Returns
        -------
        None
                
    '''
    # Create a dictionary with the article data from manual input
    article_data = {
                        'title': upload_form.title.data,
                        'subtitle': upload_form.subtitle.data,
                        'author': [
                                        {
                                            'name': author.author_name.data,
                                            'affiliation': [{'organization': aff.organization.data} for aff in author.affiliations],
                                            'email': author.email.data,
                                            'orcid': author.orcid.data if author.orcid.data != '' else None
                                        }
                                        for author in upload_form.authors
                                    ],
                        'keywords': [keyword for keyword in upload_form.keywords.data],
                        'abstract': upload_form.abstract.data,
                        'date': upload_form.date.data,
                        'volume': upload_form.volume.data,
                        'doi': upload_form.doi.data,
                        'author-short': upload_form.author_short.data
                    }
    # Alle leeren ORCID entfernen
    for author in article_data['author']:
        if author['orcid'] == None:
            del author['orcid']
    # Create a metadata.yaml file with the article data
    metadata_path = '/app/article/metadata.yaml'
    with open(metadata_path, 'w') as file:
        yaml.dump(article_data, file, default_flow_style=False, allow_unicode=True, explicit_start=True, explicit_end=True)


# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def entry():
    '''Redirects to the main route /home.'''
    return redirect(url_for('index'))

# This is the main route which is also used to create the output files
@app.route('/home', methods=['GET', 'POST'])
def index():
    '''Main route for the web interface. This route is used to create the output files.'''
    # Create form
    upload_form = UploadForm()
    # Create
    # POST request for UploadForm
    if upload_form.validate_on_submit():
        # Get the uploaded files, filters, and output formats
        markdown_file = upload_form.markdown.data
        metadata_file = upload_form.metadata.data
        bibtex_file = upload_form.bibtex.data
        images = upload_form.images.data
        file_name = upload_form.file_name.data
        selected_filters = []
        if upload_form.filter_selection.data:
            selected_filters = [filter.get("file_name") for filter in upload_form.filter_selection.data if filter.get("selected", False) == True]
        
        # Get the selected output formats
        OUTPUT_FORMATS = []
        if upload_form.pdf.data:
            OUTPUT_FORMATS.append("--pdf")
        if upload_form.html.data:
            OUTPUT_FORMATS.append("--html")
        if upload_form.jats.data:
            OUTPUT_FORMATS.append("--jats")
        if upload_form.latex.data:
            OUTPUT_FORMATS.append("--tex")
        if file_name:
            OUTPUT_FORMATS.append("--filename")
            OUTPUT_FORMATS.append(file_name)

        # If no output format is selected, return an error message
        if not OUTPUT_FORMATS:
            flash("Please select at least one output format!", "error")
            return redirect(url_for('index'))

        # Manual data input is selected
        # Create a metadata.yaml file with the data from the form
        if upload_form.manual_data_input.data:
            create_metadata_yaml_from_input(upload_form)
            METADATA_FILENAME = 'metadata.yaml'
        else: # Metadata file is uploaded
            # Save the metadata file
            # Create paths for the files
            metadata_path = os.path.join('/app/article', metadata_file.filename)
            metadata_file.save(metadata_path)
            METADATA_FILENAME = metadata_file.filename
        # Continue with the other files
        markdown_path = os.path.join('/app/article', markdown_file.filename)
        if bibtex_file:
            bibtex_path = os.path.join('/app/article', bibtex_file.filename)
        # We can save the images directly in the article folder since we don't need the filenames or paths
        if images:
            for image in images:
                image.save(os.path.join('/app/article', image.filename))
        # Save the files
        markdown_file.save(markdown_path)
        if bibtex_file:
            bibtex_file.save(bibtex_path)
        # If a bibtex file is provided, call the typesetting container with the bibtex file    
        if bibtex_file:
            # Check if filters are provided
            if selected_filters != []:
                COMMAND = ['python3', 'md2files.py', markdown_file.filename, METADATA_FILENAME, "--bibtex", bibtex_file.filename, '--filter', *selected_filters, *OUTPUT_FORMATS]
                result = subprocess.run(
                    COMMAND,
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['python3', 'md2files.py', markdown_file.filename, METADATA_FILENAME, "--bibtex", bibtex_file.filename, *OUTPUT_FORMATS],
                    capture_output=True, text=True
                )
        else:
            # Check if filters are provided
            if selected_filters:
                COMMAND = ['python3', 'md2files.py', markdown_file.filename, METADATA_FILENAME, '--filter', *selected_filters, *OUTPUT_FORMATS]
                result = subprocess.run(
                    COMMAND,
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['python3', 'md2files.py', markdown_file.filename, METADATA_FILENAME, *OUTPUT_FORMATS],
                    capture_output=True, text=True
                )

        # Create a ZIP file with the output files
        memory_file = BytesIO()

        # Write the files to the ZIP file
        ALLOWED_EXTENSIONS = {'html', 'pdf', 'xml', 'log', 'tex', 'jats', 'yaml'}
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in os.listdir('/app/article'):
                if file.split('.')[-1] in ALLOWED_EXTENSIONS:
                    zf.write(os.path.join("/app/article", file), file)
        
        # Reset the file pointer to the beginning
        memory_file.seek(0)

        # Delete the files in the article folder
        for file in os.listdir('/app/article'):
            os.remove(os.path.join('/app/article', file))

        return send_file(
            memory_file,
            as_attachment=True,
            download_name='files.zip',
            mimetype='application/zip'
        )
    # GET request
    else:
        # Get all Lua-filter in the filter folder
        filter_folder = '/app/filter'
        filter_names = os.listdir(filter_folder)
        filter_names = [filter for filter in filter_names if filter.endswith('.lua')]
        # Add filter files to the form
        for filter in filter_names:
            file_form = upload_form.filter_selection.append_entry()
            file_form.selected.label.text = filter  # Set the label to the file name
            file_form.file_name.data = filter  # Store filename or identifier if needed
        # Append random keywords
        while len(upload_form.keywords) < 3:
            keyword_entry = upload_form.keywords.append_entry()
            keyword_entry.data = "Keyword " + str(len(upload_form.keywords))
            keyword_entry.label.text = "Keyword"
        return render_template('index.html', form=upload_form)

# Route for the journal data form
# Allows the user to change the journal metadata stored in templates/MMM_JOURNAL_METADATA.yaml
@app.route('/journal_data', methods=['GET', 'POST'])
def journal_data():
    '''Route for the journal data form. This route allows the user to change the journal metadata stored in templates/MMM_JOURNAL_METADATA.yaml.'''
    # Create form
    form = JournalDataForm()
    # Load the journal data from the metadata file
    with open('/app/templates/MMM_JOURNAL_METADATA.yaml', 'r') as file:
        metadata_yaml = yaml.safe_load(file)
    if form.validate_on_submit():
        # Change these fields in the metadata file
        metadata_yaml['journal']['publisher-id'] = form.publisher_id.data
        metadata_yaml['journal']['eissn'] = form.eissn.data
        metadata_yaml['journal']['title'] = form.title.data
        metadata_yaml['journal']['publisher-name'] = form.publisher_name.data
        metadata_yaml['journal']['publisher-loc'] = form.publisher_loc.data
        metadata_yaml['journal']['link'] = form.journal_link.data
        metadata_yaml['license']['text'] = form.license_text.data
        metadata_yaml['license']['type'] = form.license_type.data
        metadata_yaml['license']['link'] = form.license_link.data
        metadata_yaml['copyright']['holder'] = form.copyright_holder.data
        # Write the changes to the metadata file
        with open('/app/templates/MMM_JOURNAL_METADATA.yaml', 'w') as file:
            yaml.dump(metadata_yaml, file, default_flow_style=False, allow_unicode=True, explicit_start=True, explicit_end=True)
        flash("Journal data updated!", "success")
        return redirect(url_for('journal_data'))
    else:
        # Load the journal data from the metadata file
        form.publisher_id.data = metadata_yaml['journal']['publisher-id']
        form.eissn.data = metadata_yaml['journal']['eissn']
        form.title.data = metadata_yaml['journal']['title']
        form.publisher_name.data = metadata_yaml['journal']['publisher-name']
        form.publisher_loc.data = metadata_yaml['journal']['publisher-loc']
        form.journal_link.data = metadata_yaml['journal']['link']
        form.license_text.data = metadata_yaml['license']['text']
        form.license_type.data = metadata_yaml['license']['type']
        form.license_link.data = metadata_yaml['license']['link']
        form.copyright_holder.data = metadata_yaml['copyright']['holder']
        return render_template('journal-data.html', form=form)
    
# Route for the help page
@app.route('/help')
def help():
    '''Route for the help page.'''
    return render_template('help.html')

# Route for the imprint page
@app.route('/imprint')
def imprint():
    '''Route for the imprint page.'''
    return render_template('imprint.html')
