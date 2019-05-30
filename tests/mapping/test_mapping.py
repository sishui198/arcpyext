import os.path
import json
import arcpy
import pytest
import arcpyext

MXD_PATH = os.path.abspath("{0}/../samples/test_mapping.mxd".format(os.path.dirname(__file__)))
MXD_COMPLEX_PATH = os.path.abspath("{0}/../samples/test_mapping_complex.mxd".format(os.path.dirname(__file__)))
MXD_COMPLEX_B_PATH = os.path.abspath("{0}/../samples/test_mapping_complex_b.mxd".format(os.path.dirname(__file__)))
CLIP2_DATA_SOURCE = {
    "workspacePath": os.path.abspath("{0}/../samples/".format(os.path.dirname(__file__))),
    "datasetName": "statesp020_clip2"
}
TEST_DATA_SOURCE = {
    "workspacePath": os.path.abspath("{0}/../samples/test_data_table2.gdb".format(os.path.dirname(__file__)))
}


@pytest.fixture(scope="module")
def map_doc():
    return arcpy.mapping.MapDocument(MXD_PATH)


@pytest.mark.parametrize(
    ("data_sources", "layer_data_sources_equal", "table_data_sources_equal", "raises_ex", "ex_type"),
    [([{
        'layers': [CLIP2_DATA_SOURCE],
        'tables': [TEST_DATA_SOURCE]
    }], [False], [False], False, None), ([{
        'layers': [None],
        'tables': [None]
    }], [True], [True], False, None),
     ([{
         'layers': [],
         'tables': []
     }], [True], [True], True, arcpyext.exceptions.ChangeDataSourcesError)])
def test_change_data_sources(map_doc, data_sources, layer_data_sources_equal, table_data_sources_equal, raises_ex, ex_type):
    layers = arcpy.mapping.ListLayers(map_doc)
    old_data_sources = []

    for layer in layers:
        old_data_sources.append(layer.dataSource)

    data_tables = arcpy.mapping.ListTableViews(map_doc)
    old_table_sources = []

    for table in data_tables:
        old_table_sources.append(table.dataSource)

    if (raises_ex):
        with pytest.raises(ex_type):
            arcpyext.mapping.change_data_sources(map_doc, data_sources)
    else:
        arcpyext.mapping.change_data_sources(map_doc, data_sources)

        for idx, layer in enumerate(layers):
            if layer.isGroupLayer or not layer.supports("workspacePath"):
                continue
            assert (layer.dataSource == old_data_sources[idx]) == layer_data_sources_equal[idx]

        for idx, table in enumerate(data_tables):
            assert (table.dataSource == old_table_sources[idx]) == table_data_sources_equal[idx]


@pytest.mark.parametrize(("mxd", "raises_ex", "ex_type"), [(MXD_COMPLEX_PATH, False, None)])
def test_describe(mxd, raises_ex, ex_type):
    mxd = arcpy.mapping.MapDocument(mxd)
    result = arcpyext.mapping.describe(mxd)

    # Dataframes
    assert len(result['maps']) == 1

    # Dataframe 1
    assert len(result['maps'][0]["layers"]) == 5, "Layer count"

    # Layer 1
    assert result['maps'][0]["layers"][0]['serviceId'] == 1
    assert result['maps'][0]["layers"][0]['name'] == "Layer 1"
    assert result['maps'][0]["layers"][0]['datasetName'] == "statesp020_clip1"

    # Layer 2
    assert result['maps'][0]["layers"][1]['serviceId'] == 2
    assert result['maps'][0]["layers"][1]['name'] == "Layer 2"
    assert result['maps'][0]["layers"][1]['datasetName'] == "statesp020_clip2"

    # Layer 3
    assert result['maps'][0]["layers"][3]['serviceId'] == 3
    assert result['maps'][0]["layers"][3]['name'] == "Layer 3"
    assert result['maps'][0]["layers"][3]['datasetName'] == "statesp020_clip1"

    # Tables
    assert len(result["maps"][0]["tables"]) == 1


@pytest.mark.parametrize(("mxd_a", "mxd_b", "document_updates", "data_frame_updates", "layers_added", "layers_updated",
                          "layers_removed", "raises_ex", "ex_type"),
                         [(MXD_COMPLEX_PATH, MXD_COMPLEX_B_PATH, 0, 1, 1, 2, 1, False, None)])
def test_compare_map_documents(mxd_a, mxd_b, document_updates, data_frame_updates, layers_added, layers_updated,
                               layers_removed, raises_ex, ex_type):
    a = arcpy.mapping.MapDocument(mxd_a)
    b = arcpy.mapping.MapDocument(mxd_b)
    result = arcpyext.mapping.compare(a, b)

    document_changes = result["document"]
    data_frame_changes = result["maps"][0]["map"]
    layer_changes = result["maps"][0]["layers"]

    assert len(document_changes) == document_updates, "Expected {0} document changes".format(document_updates)
    assert len(data_frame_changes) == data_frame_updates, "Expected {0} data frame updates".format(data_frame_updates)
    assert len(layer_changes['added']) == layers_added, "Expected {0} a".format(layers_added)
    assert len(layer_changes['updated']) == layers_updated, "Expected {0} u".format(layers_updated)
    assert len(layer_changes['removed']) == layers_removed, "Expected {0} d".format(layers_removed)


@pytest.mark.parametrize(
    ("data_source_templates"),
    [
        (
            [
                {
                    "dataSource": {
                        "datasetName": "statesp020_clip2"
                    },
                    "matchCriteria": {
                        "datasetName": "STATESP020_CLIP1"
                    }
                }
            ]
        )
    ]
)
def test_create_replacement_data_sources_list(map_doc, data_source_templates):
    arcpyext.mapping.create_replacement_data_sources_list(map_doc, data_source_templates)


def test_map_is_valid():
    #TODO: Test this function. Input is map object
    pass
