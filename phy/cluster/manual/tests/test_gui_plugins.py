# -*- coding: utf-8 -*-

"""Test GUI plugins."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from pytest import yield_fixture
from numpy.testing import assert_array_equal as ae

from .conftest import _set_test_wizard
from phy.gui.tests.test_gui import gui  # noqa


#------------------------------------------------------------------------------
# Test GUI plugins
#------------------------------------------------------------------------------

@yield_fixture  # noqa
def manual_clustering(qtbot, gui, spike_clusters, cluster_metadata):
    mc = gui.attach('ManualClustering',
                    spike_clusters=spike_clusters,
                    cluster_metadata=cluster_metadata,
                    )
    _set_test_wizard(mc.wizard)

    _s = []

    # Connect to the `select` event.
    @mc.gui.connect_
    def on_select(cluster_ids, spike_ids):
        _s.append((cluster_ids, spike_ids))

    def _assert_selection(*cluster_ids):
        assert _s[-1][0] == list(cluster_ids)

    mc._assert_selection = _assert_selection

    yield mc


def test_manual_clustering_wizard(manual_clustering):
    actions = manual_clustering.actions
    wizard = manual_clustering.wizard
    _assert_selection = manual_clustering._assert_selection

    # Test cluster ids.
    ae(manual_clustering.cluster_ids, [2, 3, 5, 7])

    # Test select actions.
    actions.select([])
    _assert_selection()

    # Test wizard actions.
    actions.reset_wizard()
    assert wizard.best_list == [3, 2, 7, 5]
    assert wizard.best == 3
    _assert_selection(3)

    actions.next()
    assert wizard.best == 2
    _assert_selection(2)

    actions.last()
    assert wizard.best == 5
    _assert_selection(5)

    actions.next()
    assert wizard.best == 5
    _assert_selection(5)

    actions.previous()
    assert wizard.best == 7
    _assert_selection(7)

    actions.first()
    assert wizard.best == 3
    _assert_selection(3)

    actions.previous()
    assert wizard.best == 3
    _assert_selection(3)

    # Test pinning.
    actions.pin()
    assert wizard.match_list == [2, 7, 5]
    assert wizard.match == 2
    _assert_selection(3, 2)

    wizard.next()
    assert wizard.match == 7
    _assert_selection(3, 7)

    wizard.unpin()
    _assert_selection(3)


def test_manual_clustering_actions(manual_clustering):
    actions = manual_clustering.actions
    wizard = manual_clustering.wizard
    _assert_selection = manual_clustering._assert_selection

    # [3   , 2   , 7        , 5]
    # [None, None, 'ignored', 'good']
    actions.reset_wizard()
    actions.pin()
    _assert_selection(3, 2)

    actions.merge()  # 3 + 2 => 8
    # [8, 7, 5]
    _assert_selection(8, 7)

    wizard.next()
    _assert_selection(8, 5)

    actions.undo()
    _assert_selection(3, 2)

    actions.redo()
    _assert_selection(8, 7)

    actions.split([2, 3])  # => 9
    _assert_selection(9, 8)

    # TODO: more tests, notably with group actions and wizard
    actions.move([9], 'good')
