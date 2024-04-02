# glyptodon

Glyptodon is a manuscript annotation tool that uses [Dash](https://dash.plotly.com/), [Plotly](https://plotly.com/python/), [OpenCV](https://opencv.org/), and [NumPy](https://numpy.org/). The purpose of this tool is to create and utilize physical document transcriptions for the digital humanities.

At present, it can accept manuscript images for most image formats. It cannot use the transcriptions uploaded in xml yet, but it should be able to in future updates.

There is an algorithm for line level segmentation and preprocessing that will be integrated into the Dash GUI in later updates.

The manuscripts/datasets that this algorithm was made in mind for are:
- [HPGTR](https://github.com/vivianpl/HPGTR/tree/main)
- [EPARCHOS](https://zenodo.org/records/4095301)
- Stavronikita Monastery Greek Handwritten Document Collection:
    - [No. 53](https://zenodo.org/records/5595669)
    - [No. 79](https://zenodo.org/records/5578136)
    - [No. 114](https://zenodo.org/records/5578251)