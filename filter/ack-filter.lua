-- filter to add specific Acknowledgment style to pdf output
-- written by Thomas Jurczyk
-- acknowledgment section needs to be wrapped in a Div with class ack (::: {.ack})

function Acknowledgments(el)
    if el.classes and el.classes[1] == "ack" then
        if FORMAT:match "latex" then
            local nextBlock = el:walk {
                Header = function(header)
                  return pandoc.RawInline("latex", "\\vskip 1em\n\\small\n\\begin{spacing}{.9}\n\\noindent\\textbf{Acknowledgments}")
                end,
                Para = function(para)
                  table.insert(para.content, 1, pandoc.RawInline("latex", "\\noindent "))
                  return {para}
                end
              }
            return {nextBlock, pandoc.RawInline("latex", "\\end{spacing}")}
        end
    end
end
  
  return {
    {Div = Acknowledgments},
  }
  
  