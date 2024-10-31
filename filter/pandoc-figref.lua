-- filter to create references to images/figures in text
-- example: "For the details, see Figure @fig:figure1" (Markdown) -> "For the details, see Figure 1." (HTML/PDF).
-- where 1 is a link to the figure.
-- inspired by pandoc-fignos filter. It works with fignos common @fig:<label> syntax. However, you can use other identifiers, too.
-- currently only transformation to LaTeX/PDF & HTML
-- tested with Pandoc 3.1
-- ***
-- Copyright (C) 2023 Thomas Jurczyk
-- ***
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- GLOBAL VARIABLES

-- table to store figure-identifiers found in the AST 
figref_table = {}
-- counter used for numbering of figures
counter = 1

-- HELPER FUNCTIONS

--- Function to add a "Figure <NUMBER>:" string as pandoc.Inline Element to a pandoc.Caption element.
-- @param plain pandoc.Plain: The pandoc.Plain block from the figure.caption.long element.
-- @return pandoc.Plain: The new pandoc.Plain block for figure.caption.long, now starting with 'Figure <NUMBER>: '.
function add_figure_label_to_caption(plain)
    -- add a "Figure <NUMBER>:" tag at the beginning of a caption
    table.insert(plain.content, 1, pandoc.Str("Figure"))
    table.insert(plain.content, 2, pandoc.Space())
    table.insert(plain.content, 3, pandoc.Str(counter .. ":"))
    table.insert(plain.content, 4 ,pandoc.Space())
    return plain
end

--- Function to find the index of an element in a table. This function is used in create_refs_in_text().
-- @param element str: The element searched for in the table.
-- @param table: The table in which the element is searched for.
-- @return str or nil: The index as a STRING value. nil if element has not been found.
function find_index(element, table)
    for index, entry in ipairs(table) do
        if entry == element then
            return tostring(index)
        end
    end
    return nil
end

---Function to replace a string in the AST that matches a figure id with HTML/LaTeX links/refs.
-- @param word string: The plain string value from Cite.citations[1].id
-- @return pandoc.RawInline or nil: Either a RawInline element with HTML/LaTeX references or nil. 
function references_generator(word)
    if table_contains(figref_table, word) then
        local referenceNumber = find_index(word, figref_table)
        if FORMAT:match "html" then
            return pandoc.RawInline('html', '<a href="#'..word..'">'..referenceNumber..'</a>')
        elseif FORMAT:match "latex" then
            return pandoc.RawInline('latex', '\\ref{'..word..'}')
        end
    else
        return nil
    end
end

--- Function to check if an element (here: the identifier of a figure) exists in a table (here: the global figref_table table with figure identifiers).
-- @param table.
-- @param element: The element to search for (= the identifier used in the in-text reference).
-- @return bool
function table_contains(table, element)
    for _,value in ipairs(table) do
        if value == element then
            return true
        end
    end
    return false
end

-- MAIN FUNCTIONS

--- Checks pandoc.Figure element for identifiers; if one was found, add it to global figref_table.
-- @param figure pandoc.Figure: The pandoc.Figure element.
-- @return pandoc.Figure or nil: New pandoc.Figure element if identifier was found, else nil.
function figure_parser(figure)
    -- only exchange caption if output format is 'html' -> LaTeX output automatically adds figure-tags like "Figure 1:" to captions
    if figure.identifier then
        -- add identifier to global id-collection (used to find in-text refs)
        table.insert(figref_table, counter, figure.identifier)
        -- change figure caption in AST: add "Figure <NUMBER>: " to caption
        if FORMAT:match "html" then 
            figure.caption.long = figure.caption.long:walk {
                Plain=add_figure_label_to_caption
            }
        end
        -- increase global counter
        counter = counter + 1
        return figure
    else
        return nil
    end
end

--- Function to replace the in-text figure reference (such as @fig:fig1), which is wrapped in a pandoc.Cite element, with the matching link syntax of the output format (HTML/LaTeX).
-- @param cite pandoc.Cite: The pandoc.Cite element.
-- @return pandoc.RawInline or nil: New pandoc.RawInline element if reference was found, else nil.
function create_refs_in_text(cite)
    return references_generator(cite.citations[1].id)
end

return {
    {Figure=figure_parser},
    {Cite=create_refs_in_text}
  }