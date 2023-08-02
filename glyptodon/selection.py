# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_selection.ipynb.

# %% auto 0
__all__ = ['createManuscriptSelect', 'createSelectionInfo', 'createFinalizeSelection', 'createSelectionLayout']

# %% ../nbs/02_selection.ipynb 5
from dash import dcc, html
import dash_bootstrap_components as dbc
from .manuscriptFiles import currentManuscripts

# %% ../nbs/02_selection.ipynb 7
def createManuscriptSelect():
    manuscripts = currentManuscripts()

    selectionKey = {}
    selectionNames = []
    for manuscript in manuscripts:
        selectionNames.append(manuscript[1]["Work"])
        selectionKey[selectionNames[-1]] = manuscript

    manuscriptSelect = dbc.RadioItems(
        options=selectionNames + ["Create New Manuscript"],
        value="Stavronikita Monastery Greek handwritten document Collection no.53",
        id="manuscript-select",
    )

    return selectionKey, manuscriptSelect

# %% ../nbs/02_selection.ipynb 10
def createSelectionInfo():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H1("Selection"),
                html.P(
                    "This menu allows you to select from the currently available manuscripts or create a new manuscript. "
                    "Once you have made your selection, click the Finalize Selection button to move to the next tab."
                )
            ]
        )
    )

# %% ../nbs/02_selection.ipynb 13
def createFinalizeSelection():
    return dbc.Button("Finalize Selection", color="primary", id="finalize-selection")

# %% ../nbs/02_selection.ipynb 16
def createSelectionLayout():
    selectionKey, manuscriptSelect = createManuscriptSelect()
    layout = html.Div(
        [
            createSelectionInfo(),
            html.Br(),
            dbc.Card(
                [
                    manuscriptSelect,
                    html.Br(),
                    createFinalizeSelection(),
                ]
            ),
        ]
    )

    return selectionKey, layout
