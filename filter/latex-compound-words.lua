--- Replace intra-word hyphens with hyphenat hyphens.
--
-- PURPOSE
--
-- The regular hyphen prevents LaTeX from breaking a word at any other
-- position than the explicit hyphen. Here we search for explicit hyphens and
-- replace them with hyphens from the hyphenat package (\hyp).
--
-- This is a fork from an original filter due to Frederik Elwert. Our
-- implementation is agnostic to text language and does not register the "-
-- babel shorthand, which makes the filter more robust. It also excludes
-- elements, like Headers and Cites. 
--
-- USAGE
--
-- The filter can then be called like this:
-- pandoc -o doc.pdf --lua-filter latex-compound-words.lua doc.md
--
-- AUTHORS
--
-- Copyright 2023-2025 Ruhr-Universität Bochum (Philosophy and the Mind Sciences)
-- Copyright 2020 Frederik Elwert <frederik.elwert@rub.de>
--
-- LICENSE
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to
-- deal in the Software without restriction, including without limitation the
-- rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
-- sell copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
-- IN THE SOFTWARE.


--- Splits a string by hyphens and returns the resulting substrings as a table.
--- @param inputstr string The input string to be split.
--- @return table The table containing the substrings.
function split_hyphen(inputstr)
    local sep = '-'
    local t = {}
    for str in string.gmatch(inputstr, '([^'..sep..']+)') do
      table.insert(t, str)
    end
    return t
end

--- Function: process_hypen
--- Processes Str elements and replaces hyphens with raw LaTeX \babelhyphen{hard} between the parts.
--- @param string The Str element to be processed.
--- @return RawInline containing the processed parts with \babelhyphen{hard} inserted between them.
function process_hyphen(elem)
  local parts = split_hyphen(elem.text)
  -- if not more than one part, string contains no hyphen, return unchanged.
  if #parts <= 1 then
    return nil
  end
  -- otherwise, splice raw LaTeX \babelhyphen{hard} between parts
  local o = {}
  for index, part in ipairs(parts) do
    table.insert(o, pandoc.Str(part))
    if index < #parts then
      table.insert(o, pandoc.RawInline('latex', '\\hyp '))
    end
  end
  return o
end

-- This function is used as a filter in the Pandoc document conversion process.
-- It modifies the document's blocks by replacing hyphens in Str elements with LaTeX \babelhyphen{hard}.
-- The function ignores Cite and Link elements and excludes Headers and Meta elements from modification.
-- The modified blocks are returned as a new block.
function Para(el)
  if FORMAT:match "latex" or FORMAT:match "native" then
      local newPara = el:walk {
        traverse = "topdown",
        Cite = function(elem) return elem, false end, -- ignore citations
        Link = function(elem) return elem, false end, -- ignore links
        Str = process_hyphen, -- replace hyphens in Str elements
      }
      return newPara
    end
end
  
  return {
    {Para = Para},
  }
