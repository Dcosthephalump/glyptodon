# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_app.ipynb.

# %% auto 0
__all__ = ['selectionKey', 'selectionLayout', 'centuries', 'informationLayout', 'annotationLayout', 'exportLayout', 'app',
           'newManuscript', 'selectedManuscript', 'selectManuscript', 'finalizeSelectionCallback',
           'pageSelectorCallback', 'saveShapesCallback', 'lineNumberCallback', 'saveAnnotationCallback',
           'saveNContinuteCallback', 'nextTabCallback', 'exportManuscriptCallback']

# %% ../nbs/07_app.ipynb 4
from dash import Dash, State, Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc
from .annotation import *
from .classes import *
from .export import *
from .information import *
from .manuscriptFiles import *
from .selection import *
import re
import os

# %% ../nbs/07_app.ipynb 8
selectionKey, selectionLayout = createSelectionLayout()

centuries, informationLayout = createInformationLayout()

annotationLayout = createAnnotationLayout()

exportLayout = createExportLayout()

# %% ../nbs/07_app.ipynb 10
app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs-object",
            value="selection",
            children=[
                dcc.Tab(
                    label="Selection",
                    value="selection",
                    children=[
                        selectionLayout
                    ],
                ),
                dcc.Tab(
                    label="Information",
                    value="information",
                    children=[
                        informationLayout
                    ],
                ),
                dcc.Tab(
                    label="Annotation",
                    value="annotation",
                    children=[
                        annotationLayout
                    ],
                ),
                dcc.Tab(
                    label="Export",
                    value="export",
                    children=[
                        exportLayout
                    ],
                ),
            ],
        ),
#        html.Div(id="current-tab"),
        html.Div(
            children="no callback",
            id="dummy-output",
            style={"display": "none"},
        ),
    ]
)

# %% ../nbs/07_app.ipynb 14
newManuscript = False
selectedManuscript = selectionKey[
    "Stavronikita Monastery Greek handwritten document Collection no.53"
]

@callback(
    Output("work", "placeholder",),
    Output("author", "placeholder",),
    Output("language", "placeholder",),
    Output("country", "placeholder",),
    Output("city", "placeholder",),
    Output("institution", "placeholder",),
    Output("centuries-slider", "value",),
    Output("uploader-container","style"), # This determines if uploaders are displayed
    Input("manuscript-select", "value"),
    suppress_callback_exceptions=True,
)
def selectManuscript(work):
    global selectedManuscript
    global selectionKey
    if work == "Create New Manuscript":
        newManuscript = True
        selectedManuscript = None
        return "", "", "", "", "", "", [1, 20], {"display": "block"}
    else:
        selectedManuscript = selectionKey[work]
        work = selectedManuscript[1]["Work"]
        author = selectedManuscript[1]["Author"]
        language = selectedManuscript[1]["Language"]
        country = selectedManuscript[1]["Country"]
        city = selectedManuscript[1]["City"]
        institution = selectedManuscript[1]["Institution"]

        ### Converts the string containing centuries into list containing the centuries as integers
        # This stores the string as a list of words. There are strings with two words and four words
        centuriesAsList = selectedManuscript[1]["Centuries"].split()

        # This picks out the relevant words and strips them of everything but the integer values
        if len(centuriesAsList) == 2:
            centuriesValue = [
                int(re.sub("[^0-9]", "", centuriesAsList[0])),
                int(re.sub("[^0-9]", "", centuriesAsList[0])),
            ]
        else:
            centuriesValue = [
                int(re.sub("[^0-9]", "", centuriesAsList[0])),
                int(re.sub("[^0-9]", "", centuriesAsList[2])),
            ]
        return work, author, language, country, city, institution, centuriesValue, {"display": "none"}

# %% ../nbs/07_app.ipynb 16
@callback(
    Output("page-selector", "options"),
    Output("page-selector", "value"),
    Output("tabs-object","value", allow_duplicate=True),
    Input("finalize-selection", "n_clicks"),
    prevent_initial_call=True,
)
def finalizeSelectionCallback(clicks):
    global selectedManuscript
    dropdownOptions = []
    relativePaths = manuscriptImages(selectedManuscript[0])

    index = 1
    for path in relativePaths:
        imageName = path.split("/")[-1]
        if imageName[0] != ".":
            dropdownOptions.append({"label": f"Page {index}", "value": path})
            index = index + 1

    return dropdownOptions, dropdownOptions[0]["value"], "information"

# %% ../nbs/07_app.ipynb 18
@callback(
    Output("annotation-figure", "figure"),
    Input("page-selector", "value"),
    prevent_initial_call=True,
)
def pageSelectorCallback(path):
    global selectedManuscript
    fig = createAnnotationFigure(path)

    imageName = path.split("/")[-1]  # This takes the file name in the directory
    imageName = imageName.split(".")[0]  # This assumes

    statesDirectory = os.path.join(selectedManuscript[0], "states")
    linesDirectory = os.path.join(statesDirectory, "lines")
    bboxesDirectory = os.path.join(statesDirectory, "bboxes")
    
    # Instantiate lines from csv and add them to figure
    for file in os.listdir(linesDirectory):
        fileName = file.split(".")[0]
        if fileName == imageName:
            figLines = Line.csvToLines(os.path.join(linesDirectory, file))

            for line in figLines:
                fig.add_shape(
                    editable = True,
                    type=line.type,
                    x0=line.x0,
                    y0=line.y0,
                    x1=line.x1,
                    y1=line.y1,
                    line=line.line,
                    opacity=line.opacity,
                )

    # Instantiate bboxes from csv and add them to figure
    for file in os.listdir(bboxesDirectory):
        fileName = file.split(".")[0]
        if fileName == imageName:
            figBBoxes = BBox.csvToBBoxes(os.path.join(bboxesDirectory, file))
            
            for bbox in figBBoxes:
                fig.add_shape(
                    editable = True,
                    type=bbox.type,
                    x0=bbox.x0,
                    y0=bbox.y0,
                    x1=bbox.x1,
                    y1=bbox.y1,
                    line=bbox.line,
                    opacity=bbox.opacity,
                )

    return fig

# %% ../nbs/07_app.ipynb 20
@callback(
    Output("dummy-output","children", allow_duplicate=True),
    Input("save-shapes", "n_clicks"),
    State("annotation-figure", "relayoutData"),
    State("page-selector", "value"),
    prevent_initial_call=True,
)
def saveShapesCallback(clicks, shapes, path):
    global selectedManuscript
    dictLines = []
    dictBBoxes = []
    for shape in shapes["shapes"]:
        if shape["type"] == "line":
            dictLines.append(shape)
        if shape["type"] == "rect":
            dictBBoxes.append(shape)
    
    lines = []
    for line in dictLines:
        lines.append(
            Line(
                x0=line["x0"],
                y0=line["y0"],
                x1=line["x1"],
                y1=line["y1"],
            )
        )
    Line.sortLines(lines)
    
    tempBBoxes = []
    for bbox in dictBBoxes:
        tempBBoxes.append(
            BBox(
                x0=int(bbox["x0"]),
                y0=int(bbox["y0"]),
                x1=int(bbox["x1"]),
                y1=int(bbox["y1"]),
            )
        )

    bboxes = []
    for line in lines:
        bboxes.append([])
        for bbox in tempBBoxes:
            if bbox.isLine(line):
                bboxes[-1].append(bbox)

    flattenedBBoxes = []
    for line in bboxes:
        BBox.sortBBoxes(line)
        flattenedBBoxes = flattenedBBoxes + line

    imageName = path.split("/")[-1]
    imageName = imageName.split(".")[0]

    statesDirectory = os.path.join(selectedManuscript[0], "states")
    linesDirectory = os.path.join(statesDirectory, "lines")
    bboxesDirectory = os.path.join(statesDirectory, "bboxes")

    Line.linesToCSV(linesDirectory, lines, imageName)
    BBox.bboxesToCSV(bboxesDirectory, flattenedBBoxes, imageName)
    
    dummy = ["1","2","3"]
    return dummy

# %% ../nbs/07_app.ipynb 22
@callback(
    Output("annotation-text-area","value"),
    Input("annotation-figure", "relayoutData"),
    State("annotation-text-area","value"),
    prevent_initial_call=True,
)
def lineNumberCallback(shapes, currentText):
    numLines = 0
    for shape in shapes["shapes"]:
        if shape["type"] == "line":
            numLines = numLines + 1
    
    currentLines = currentText.split("\n")
    newLines = []
    for i in range(1,numLines+1):
        if i > len(currentLines):
            if i < 10:
                newLines.append(f"0{i}:\n")
            else:
                newLines.append(f"{i}:\n")
        else:
            if currentLines[i-1][0:2].isnumeric() and int(currentLines[i-1][0:2]) == i:
                newLines.append(currentLines[i-1] + "\n")
            elif i < 10:
                newLines.append(f"0{i}:\n")
            else:
                newLines.append(f"{i}:\n")
    
    newValue = ""
    for line in newLines:
        newValue = newValue + line
    
    return newValue

# %% ../nbs/07_app.ipynb 24
@callback(
    Output("dummy-output", "children", allow_duplicate=True),
    Input("save-annotation", "n_clicks"),
    State("annotation-figure", "relayoutData"),
    State("page-selector", "value"),
    State("annotation-text-area", "value"),
    prevent_initial_call=True,
)
def saveAnnotationCallback(clicks, shapes, path, currentText):
    global selectedManuscript
    dictLines = []
    dictBBoxes = []
    for shape in shapes["shapes"]:
        if shape["type"] == "line":
            dictLines.append(shape)
        if shape["type"] == "rect":
            dictBBoxes.append(shape)

    currentLines = currentText.split("\n")
    currentWords = []
    for line in currentLines:
        currentWords.append(line[4:].split(" "))

    lines = []
    for line in dictLines:
        lines.append(
            Line(
                x0=line["x0"],
                y0=line["y0"],
                x1=line["x1"],
                y1=line["y1"],
            )
        )
    Line.sortLines(lines)

    for line in lines:
        line.text = currentLines[line.index - 1][4:]

    tempBBoxes = []
    for bbox in dictBBoxes:
        tempBBoxes.append(
            BBox(
                x0=int(bbox["x0"]),
                y0=int(bbox["y0"]),
                x1=int(bbox["x1"]),
                y1=int(bbox["y1"]),
            )
        )

    bboxes = []
    for line in lines:
        bboxes.append([])
        for bbox in tempBBoxes:
            if bbox.isLine(line):
                bboxes[-1].append(bbox)

    flattenedBBoxes = []
    for line in bboxes:
        BBox.sortBBoxes(line)
        flattenedBBoxes = flattenedBBoxes + line

    for line in bboxes:
        if len(line) == 0:
            pass
        elif len(line) == len(currentWords[line[0].lineNo - 1]):
            for bbox in line:
                bbox.annotation = currentWords[bbox.lineNo - 1][bbox.index - 1]

    imageName = path.split("/")[-1]
    imageName = imageName.split(".")[0]

    statesDirectory = os.path.join(selectedManuscript[0], "states")
    linesDirectory = os.path.join(statesDirectory, "lines")
    bboxesDirectory = os.path.join(statesDirectory, "bboxes")

    Line.linesToCSV(linesDirectory, lines, imageName)
    BBox.bboxesToCSV(bboxesDirectory, flattenedBBoxes, imageName)

    dummy = ["1", "2", "3"]
    return dummy

# %% ../nbs/07_app.ipynb 26
@callback(
    Output("tabs-object", "value", allow_duplicate=True),
    Output("manuscript-select", "value"),
    Output("manuscript-select", "options"),
    Input("save-and-continue", "n_clicks"),
    # Input objects
    State("work", "placeholder"),
    State("author", "placeholder"),
    State("language", "placeholder"),
    State("country", "placeholder"),
    State("city", "placeholder"),
    State("institution", "placeholder"),
    State("centuries-slider", "value"),
    # Upload objects
    State("upload-images", "contents"),
    State("upload-images", "filename"),
    State("upload-manuscripts","contents"),
    State("upload-manuscripts","filename"),
    # Conditional object
    State("manuscript-select", "value"),
    State("manuscript-select", "options"),
    prevent_initial_call=True,
)
def saveNContinuteCallback(
    clicks, # Input save-and-continue
    work, # State work
    author, # State author
    language, # State language
    country, # State country
    city, # State city
    institution, # State institution
    centuriesValue, # State centuries-slider
    imContents, # State upload-images
    imFilenames, # State upload-images
    manContents, # State upload-manuscripts
    manFilenames, # State upload-manuscripts
    manSelectVal, # State manuscript-select value
    manSelectOpts, # State manuscript select options
):
    global selectedManuscript
    global centuries
    global selectionKey
    centuriesData = ""
    if centuriesValue[0] == centuriesValue[1]:
        centuriesData = centuries[centuriesValue[0]] + " Century"
    else:
        centuriesData = (
            centuries[centuriesValue[0]]
            + " to "
            + centuries[centuriesValue[1]]
            + " Centuries"
        )
    
    print(work)
    print(author)
    print(language)
    print(country)
    print(city)
    print(institution)
    print(centuriesData)
    
    information = {
        "Work": work,
        "Author": author,
        "Language": language,
        "Country": country,
        "City": city,
        "Institution": institution,
        "Centuries": centuriesData,
    }

    print(information)
    if manSelectVal == "Create New Manuscript":
        selectedManuscript = (createManuscriptDirectory(information), information)
        saveImages(imContents, imFilenames, selectedManuscript[0])
        saveTranscripts(manContents, manFilenames, selectedManuscript[0])
        
        manuscripts = currentManuscripts()
        
        selectionKey = {}
        selectionNames = []
        for manuscript in manuscripts:
            selectionNames.append(manuscript[1]["Work"])
            selectionKey[selectionNames[-1]] = manuscript
        
        manSelectVal = information["Work"]
        manSelectOpts = selectionNames + ["Create New Manuscript"]
        
        return "annotation", manSelectVal, manSelectOpts
    else:
        updateMetadata(selectedManuscript[0], information)
        
        return "annotation", manSelectVal, manSelectOpts

# %% ../nbs/07_app.ipynb 28
@callback(
    Output("tabs-object", "value", allow_duplicate=True),
    Input("next-tab", "n_clicks"),
    prevent_initial_call=True,
)
def nextTabCallback(clicks):
    return "export"

# %% ../nbs/07_app.ipynb 30
@callback(
    Output("export-download", "data"),
    Input("export-button", "n_clicks"),
    State("export-name", "value"),
    State("directory-options", "value"),
    prevent_initial_call=True,
)
def exportManuscriptCallback(clicks, name, options):
    global selectedManuscript
    path = zipManuscript(options, selectedManuscript[0], name)
    return dcc.send_file(path)

# %% ../nbs/07_app.ipynb 32
if __name__ == "__main__":
    app.run(debug=True)
