$(document).ready(function () {
    // Deactivate manual data input if metadata file is uploaded
    $('#manual_data_input').change(function () {
        if ($(this).is(':checked')) {
            $('#mmm-ts-article-data-container').show();
            $('#metadata_upload').prop('disabled', true);
        } else {
            $('#mmm-ts-article-data-container').hide();
            $('#metadata_upload').prop('disabled', false);
        }
    });

    // Add author
    $('#add-author').click(function () {
        var index = $('#authors .author').length;
        var new_author = `
    <div class="mt-2 form-group author">
        <h3>Author ${index + 1}</h3>
        <div>
            <label for="authors-${index}-author_name" class="mt-2">Name</label><br>
            <input form="ArticleDataForm" id="authors-${index}-author_name" name="authors-${index}-author_name" size="50"
                type="text" value="">
        </div>
        <div>
            <label for="authors-${index}-email" class="mt-2">E-Mail</label><br>
            <input form="ArticleDataForm" id="authors-${index}-email" name="authors-${index}-email" size="50" type="email"
                value="">
        </div>
        <div>
            <label for="authors-${index}-orcid" class="mt-2">ORCID</label><br>
            <input form="ArticleDataForm" id="authors-${index}-orcid" name="authors-${index}-orcid" size="20" type="text"
                value="">
        </div>
        <div>
            <h4 class="mt-3">Affiliations</h4>
            <div class="affiliations">
                <div class="form-group affiliation mt-2">
                    <label for="authors-${index}-affiliations-0-organization">Organization</label><br>
                    <input form="ArticleDataForm" id="authors-${index}-affiliations-0-organization"
                        name="authors-${index}-affiliations-0-organization" size="50" type="text" value="">
                    <span class="remove-affiliation remove-button btn btn-outline-danger btn-sm">Remove</span>
                </div>
            </div>
            <button type="button" class="add-affiliation btn btn-outline-success btn-sm mt-2">Add affiliation</button>
        </div>
        <span class="remove-author remove-button btn btn-outline-danger mt-2 btn-sm">Remove author</span>
    </div>
    `;
        $('#authors').append(new_author);
        // Author index-attributes need to be updated
        $('#authors .author').each(function (i) {
            // Find all input elements whose id starts with "keywords-"
            $(this).find('input[id^="authors-"]').each(function (j) {
                // Update the id and name  for each matching input
                // get the id value
                var id = $(this).attr('id');
                // Split the id value by "-"
                var id_parts = id.split('-');
                // Replace the second part with the new index
                id_parts[1] = i;
                // Join the parts back together
                var new_id = id_parts.join('-');
                // Set the new id value
                $(this).attr('id', new_id);
                // Replace the name attribute
                $(this).attr('name', new_id);
                // Find the label element and update the for attribute
                $(this).siblings('label').attr('for', new_id);
            });
            // Update the author h3 header
            $(this).find('h3').text('Author ' + (i + 1));
        });
    });

    // Remove author
    $('#authors').on('click', '.remove-author', function () {
        $(this).closest('.author').remove();
    });

    // Add affiliation
    $('#authors').on('click', '.add-affiliation', function () {
        var author_section = $(this).closest('.author');
        var affiliations = author_section.find('.affiliations');
        var index = affiliations.find('.affiliation').length;
        var author_index = $('#authors .author').index(author_section);
        var new_affiliation = `
    <div class="form-group affiliation mt-2">
        <label>Organization</label><br>
        <input form="ArticleDataForm" id="authors-${author_index}-affiliations-${index}-organization"
            name="authors-${author_index}-affiliations-${index}-organization" size="50" type="text" value="">
        <span class="remove-affiliation remove-button btn btn-outline-danger btn-sm">Remove</span>
    </div>
    `;
        affiliations.append(new_affiliation);
        // Affiliation index-attributes need to be updated
        affiliations.find('.affiliation').each(function (i) {
            // Find all input elements whose id starts with "keywords-"
            $(this).find('input[id^="authors-"]').each(function (j) {
                // Update the id and name  for each matching input
                // get the id value
                var id = $(this).attr('id');
                // Split the id value by "-"
                var id_parts = id.split('-');
                // Replace the second part with the new index
                id_parts[3] = i;
                // Join the parts back together
                var new_id = id_parts.join('-');
                // Set the new id value
                $(this).attr('id', new_id);
                // Replace the name attribute
                $(this).attr('name', new_id);
            });
        });
    });

    // Remove affiliation
    $('#authors').on('click', '.remove-affiliation', function () {
        $(this).closest('.affiliation').remove();
    });

    // Add keywords
    $('#add-keyword').click(function () {
        var index = $('#keywords .keyword').length;
        var new_keyword = `
    <div class="mt-2 form-group keyword">
        <label for="keywords-${index}">Keyword</label><br>
        <input form="ArticleDataForm" id="keywords-${index}" name="keywords-${index}" size="50" type="text" value="">
        <span class="remove-keyword remove-button btn btn-outline-danger btn-sm">Remove</span>
    </div>
    `;
        $('#keywords').append(new_keyword);
        // Keyword name attributes need to be updated
        $('#keywords .keyword').each(function (i) {
            $(this).find('input').attr('id', 'keywords-' + i);
            $(this).find('input').attr('name', 'keywords-' + i);
            $(this).find('label').attr('for', 'keywords-' + i);
        });
    });

    // Remove keywords
    $('#keywords').on('click', '.remove-keyword', function () {
        $(this).closest('.keyword').remove();
    });
});
