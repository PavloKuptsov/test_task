"Smart XML Analyzer" Test task

The algorithm gets the information about HTML element from the original file, namely its attributes.

Then The algotith scans different page, finds all the elements with corresponding tags. After that algorithm compares found elements' attributes with the ones of the original element, adding "weight points" on every found matches. 
All attributes weigh 1 point, except for "id", and "content" (writing on the button), which weigh more.
The reasoning behind this is that ID is uniwue, and if it matches - it must be the same button, while the button with the same writing on it also must be the same as original even if it has different other attributes.
