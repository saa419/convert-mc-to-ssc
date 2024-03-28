import json
import simfile
from simfile.notes import Note, NoteType, NoteData
from simfile.timing import Beat
import bisect

# Filepath to mc file to be converted
mc_path = 'malodyfile.mc'
# Sample ssc file, preloaded with song info and a blank chart
ssc_path = 'sample.ssc'
# New ssc file to save
newssc_path = 'output.ssc'
# Open the sample ssc file
sscfile = simfile.open(ssc_path)
# Load the existing chart. The first one will be replaced
chart = sscfile.charts[0]
# This is for a singles chart. For doubles, change this to 8
cols = 4
convnotes = []

# Open the Malody mc (JSON) file and load the data
with open(mc_path, 'r') as file:
    data = json.load(file)

# Read the note data in the mc file. I forget why I called the individual note info "thing", but we're rolling with that
for thing in data["note"]:
    # Skip the last entry in the note data, which is the song file info
    if "type" in thing:
        break
    else:
        # First, we'll process hold notes, mapping the start and end of the hold notes
        if "endbeat" in thing:
            addhold = Note(
                # The '+(thing["beat"][1]/thing["beat"][2])' part looks slightly convoluted, but it's to process anything beyond quarter notes. These get stored by Malody according to the note snap that was in place when the note was placed in the editor, but dividing these two values gives the right note
                    beat=Beat(thing["beat"][0]+(thing["beat"][1]/thing["beat"][2])),
                    column=thing["column"],
                    note_type=NoteType.HOLD_HEAD,
                )
            # We need to account for jumps and holds, which have different arrow data slightly out of order in the mc file. The following bisect thing is a Python module that allows the arrow data to be placed in sorted order within the list representing the notes
            # Find the insertion point for the new tuple based on the first item
            insertion_index = bisect.bisect_left([item[0] for item in convnotes], addhold[0])
#           # Insert the new tuple into the list at the determined position
            convnotes.insert(insertion_index, addhold)
            # The end of the hold note (the tail) has its timing info stored separately, so do the same thing for these
            addtail = Note(
                    beat=Beat(thing["endbeat"][0]+(thing["endbeat"][1]/thing["endbeat"][2])),
                    column=thing["column"],
                    note_type=NoteType.TAIL,
                )
            # Find the insertion point for the new tuple based on the first item
            insertion_index = bisect.bisect_left([item[0] for item in convnotes], addtail[0])
#           # Insert the new tuple into the list at the determined position
            convnotes.insert(insertion_index, addtail)
        else:
            # If not a hold note, then a regular note. Process these separately, as described above with the heads/tails of the hold note
            addnote = Note(
                    beat=Beat(thing["beat"][0]+(thing["beat"][1]/thing["beat"][2])),
                    column=thing["column"],
                    note_type=NoteType.TAP,
                )
            # Find the insertion point for the new tuple based on the first item
            insertion_index = bisect.bisect_left([item[0] for item in convnotes], addnote[0])
#           # Insert the new tuple into the list at the determined position
            convnotes.insert(insertion_index, addnote)
# These next 3 lines put the converted note data back into the SM/SSC simfile format
note_data = NoteData.from_notes(convnotes, cols)
chart.notes = str(note_data)
sscfile.charts[0] = chart
# Save the new output file and done!
with open(newssc_path, 'w', encoding='utf-8') as outfile:
    sscfile.serialize(outfile)
