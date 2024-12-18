-- Filter to add # Acknowledgment { .unnumbered } to Markdown if this line is missing
-- Written by Thomas Jurczyk
-- Acknowledgment section needs to be wrapped in a Div with class ack (::: {.ack})


-- Function to check if a string is in a list of strings
function is_string_in_list(target_string, string_list)
  for _, str in ipairs(string_list) do
      if str == target_string then
          return true
      end
  end
  return false
end

-- Main function to add potentially missing Header class .unnumbered to Acknowledgment section header
function Acknowledgments(el)
    if el.classes and el.classes[1] == "ack" then
        local nextBlock = el:walk {
            Header = function(header)
              -- Check if the header is already unnumbered
              if is_string_in_list("unnumbered", header.classes) then
                return header
              else -- If not, add the unnumbered class
                table.insert(header.classes, "unnumbered")
                return header
              end
            end
          }
        return {nextBlock}
    end
end
  
return {
  {Div = Acknowledgments},
}
  
  