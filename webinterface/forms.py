'''
This module contains the FlaskForm classes used in the web interface of the typesetting tool.
'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField, FileAllowed, MultipleFileField
from wtforms import SubmitField, FieldList, FormField, BooleanField, HiddenField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, URL, Optional

class AffiliationForm(FlaskForm):
    """
    A form for capturing affiliation information.

    Attributes
    ----------
    organization: StringField
        An optional field to input the name of the organization.
    """
    organization = StringField('Organization', validators=[Optional()])

class AuthorForm(FlaskForm):
    """
    AuthorForm is a FlaskForm that collects information about an author.

    Attributes
    ----------
    author_name : StringField
        The name of the author. This field is optional.
    affiliations : FieldList
        A list of affiliations for the author, containing a minimum of 1 and a maximum of 3 AffiliationForm entries.
    email : StringField
        The email address of the author. This field is optional.
    orcid : StringField
        The ORCID identifier of the author. This field is optional.
    """
    author_name = StringField('Name', validators=[Optional()])
    affiliations = FieldList(FormField(AffiliationForm), min_entries=1, max_entries=3)
    email = StringField('E-Mail', validators=[Optional()])
    orcid = StringField('ORCID', validators=[Optional()])

class FilterSelectionForm(FlaskForm):
    """
    FilterSelectionForm is a form used in a Flask web application to handle filter selections.

    Attributes
    ----------
    selected: BooleanField
        A boolean field that indicates whether any filters are selected. Defaults to "No filters found!".

        .. :no-index:
        
    file_name: HiddenField
        A hidden field used to store the file name and pass this value to the MMM script. This is a workaround since passing the value via BooleanField was not possible due to HTML limitations with FieldList.

        .. :no-index:

    Note
    ----
        FieldList cannot enclose BooleanField or SubmitField instances due to HTML limitations.
        For more information, see: https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.FieldList
    """
    selected = BooleanField("No filters found!")
    # The hidden field is used to store the file name and to pass this value to the MMM script.
    # This is a workaround since passing the value via BooleanField was not possible, see also FieldList docs:
    # "Note: Due to a limitation in how HTML sends values, FieldList cannot enclose BooleanField or SubmitField instances."
    # https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.FieldList
    file_name = HiddenField()

class JournalDataForm(FlaskForm):
    """
    JournalDataForm is a FlaskForm for collecting and validating journal-related data.

    Attributes
    ----------
    publisher_id : StringField
        The ID of the publisher. Required.
    eissn : StringField
        The electronic ISSN of the journal. Required.
    title : StringField
        The title of the journal. Required.
    publisher_name : StringField
        The name of the publisher. Required.
    publisher_loc : StringField
        The location of the publisher. Required.
    journal_link : StringField
        The URL link to the journal. Required and must be a valid URL.
    license_text : TextAreaField
        The text of the license. Required.
    license_type : StringField
        The type of the license. Required.
    license_link : StringField
        The URL link to the license. Required and must be a valid URL.
    copyright_holder : StringField
        The holder of the copyright. Required.
    submit : SubmitField
        The submit button to update the form.
    """
    # Journal section
    publisher_id = StringField('Publisher ID', validators=[DataRequired()])
    eissn = StringField('EISSN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    publisher_name = StringField('Publisher Name', validators=[DataRequired()])
    publisher_loc = StringField('Publisher Location', validators=[DataRequired()])
    journal_link = StringField('Journal Link', validators=[DataRequired(), URL()])
    
    # License section
    license_text = TextAreaField('License Text', validators=[DataRequired()])
    license_type = StringField('License Type', validators=[DataRequired()])
    license_link = StringField('License Link', validators=[DataRequired(), URL()])
    
    # Copyright section
    copyright_holder = StringField('Copyright Holder', validators=[DataRequired()])
    
    # Submit button
    submit = SubmitField('Update!')

class UploadForm(FlaskForm):
    """
    UploadForm is a FlaskForm that handles the upload and input of various files and metadata for typesetting.

    Attributes
    ----------
    markdown : FileField
        Required field for uploading a Markdown file. Only accepts files with extensions 'md' or 'markdown'.
    metadata : FileField
        Optional field for uploading a metadata file. Only accepts files with extensions 'yaml' or 'yml'.
    bibtex : FileField
        Optional field for uploading a BibTeX file. Only accepts files with extension 'bib'.
    images : MultipleFileField
        Optional field for uploading multiple image files. Only accepts files with extensions 'png', 'jpg', or 'jpeg'.
    filter_selection : FieldList
        Dynamic form field for selecting filters. Displays all filters in the filter folder.
    file_name : StringField
        Optional field for specifying individual file names.
    pdf : BooleanField
        Checkbox to select PDF output.
    html : BooleanField
        Checkbox to select HTML output.
    jats : BooleanField
        Checkbox to select JATS output.
    latex : BooleanField
        Checkbox to select LaTeX output.
    manual_data_input : BooleanField
        Checkbox to activate manual data input instead of uploading a metadata file.
    submit : SubmitField
        Button to submit the form and create files.

    Optional Metadata Fields (used if no metadata file is uploaded)
    ---------------------------------------------------------------
    title : StringField
        Optional field for the article title.
    subtitle : StringField
        Optional field for the article subtitle.
    keywords : FieldList
        Optional field for article keywords. Can have between 1 and 8 entries, each being a StringField.
    abstract : TextAreaField
        Optional field for the article abstract.
    date : StringField
        Optional field for the article year.
    volume : IntegerField
        Optional field for the article volume.
    doi : StringField
        Optional field for the article DOI.
    author_short : StringField
        Optional field for a short author description.
    authors : FieldList
        Optional field for author data. Can have between 1 and 20 entries, each being an AuthorForm.
    """

    markdown = FileField('Markdown file (required)', validators=[FileRequired(), FileAllowed(["md", "markdown"])])
    metadata = FileField('Metadata file (optional)', validators=[FileAllowed(["yaml", "yml"])])
    bibtex = FileField('BibTeX file (optional)', validators=[FileAllowed(["bib"])])
    images = MultipleFileField('Select image files (PNG, JPG) (optional)', validators=[FileAllowed(["png", "jpg", "jpeg"])])
    # Dynamic form field for filters
    # Displays all filters in the filter folder
    filter_selection = FieldList(FormField(FilterSelectionForm))
    # StringField to pass individual file names
    file_name = StringField('Name output files (optional)')
    # BooleandField to select PDF output
    pdf = BooleanField('PDF')
    # BooleandField to select HTML output
    html = BooleanField('HTML')
    # BooleanField to select JATS output
    jats = BooleanField('JATS')
    # BooleanField to select LaTeX output
    latex = BooleanField('LaTeX')
    # Select if metadata yaml upload or manual data input should be activated
    manual_data_input = BooleanField('(Optional) Manual data input')
    # Submit button
    submit = SubmitField('Create files!')
    ### The following fields are optional and are used if no metadata file is uploaded
    # Article data
    title = StringField('Title', validators=[Optional()])
    subtitle = StringField('Subtitle', validators=[Optional()])
    keywords = FieldList(StringField('Keyword', validators=[Optional()], default="Keyword"), min_entries=1, max_entries=8)
    abstract = TextAreaField('Abstract', validators=[Optional()], default="Your abstract goes here...")
    date = StringField('Year', validators=[Optional()])
    volume = IntegerField('Volume', validators=[Optional()])
    doi = StringField('DOI', validators=[Optional()])
    # Author data
    author_short = StringField('Author short', validators=[Optional()])
    authors = FieldList(FormField(AuthorForm), min_entries=1, max_entries=20)