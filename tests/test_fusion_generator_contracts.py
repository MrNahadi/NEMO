import importlib.util
import sys
import types
from pathlib import Path

import pytest


class _Collection(list):
    @classmethod
    def create(cls):
        return cls()

    @property
    def count(self):
        return len(self)

    def add(self, value):
        self.append(value)


class _ValueInput:
    @staticmethod
    def createByReal(value):
        return value


@pytest.fixture
def fusion_generators(monkeypatch):
    core = types.ModuleType("adsk.core")
    core.ObjectCollection = _Collection
    core.ValueInput = _ValueInput
    fusion = types.ModuleType("adsk.fusion")
    fusion.FeatureOperations = types.SimpleNamespace(
        JoinFeatureOperation="join",
    )
    adsk = types.ModuleType("adsk")
    adsk.core = core
    adsk.fusion = fusion
    monkeypatch.setitem(sys.modules, "adsk", adsk)
    monkeypatch.setitem(sys.modules, "adsk.core", core)
    monkeypatch.setitem(sys.modules, "adsk.fusion", fusion)

    path = (
        Path(__file__).parents[1]
        / "fusion_addin"
        / "NEMOBridge"
        / "fusion_generators.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_nemo_test_fusion_generators", path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _BodyCollection:
    def __init__(self, bodies):
        self._bodies = list(bodies)

    @property
    def count(self):
        return len(self._bodies)

    def item(self, index):
        return self._bodies[index]


class _Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class _BoundingBox:
    def __init__(self, minimum, maximum):
        self.minPoint = _Point(*minimum)
        self.maxPoint = _Point(*maximum)


class _Edge:
    def __init__(self, minimum, maximum):
        self.boundingBox = _BoundingBox(minimum, maximum)


def test_join_body_uses_explicit_boolean_join(fusion_generators):
    result_body = object()
    feature = types.SimpleNamespace(
        name=None,
        bodies=_BodyCollection([result_body]),
    )

    class CombineFeatures:
        def createInput(self, target, tools):
            self.input = types.SimpleNamespace(
                target=target,
                tools=tools,
                operation=None,
                isKeepToolBodies=True,
            )
            return self.input

        def add(self, input_):
            assert input_ is self.input
            return feature

    combine_features = CombineFeatures()
    component = types.SimpleNamespace(
        features=types.SimpleNamespace(combineFeatures=combine_features)
    )
    target = object()
    tool = object()

    result = fusion_generators._join_body(component, target, tool, "Join lug")

    assert result is result_body
    assert combine_features.input.target is target
    assert combine_features.input.tools == [tool]
    assert combine_features.input.operation == "join"
    assert combine_features.input.isKeepToolBodies is False
    assert feature.name == "Join lug"


def test_padeye_crown_is_circular_and_tangent_to_tapered_side(
    fusion_generators,
):
    geometry = fusion_generators._padeye_lug_geometry(
        base_thickness=1.4,
        join_overlap=0.02,
        lug_height=18.0,
        neck_width=10.0,
        root_width=18.0,
    )

    radius_x = geometry["tangent_x"]
    radius_z = geometry["tangent_z"] - geometry["center_z"]
    side_x = geometry["tangent_x"] - 9.0
    side_z = geometry["tangent_z"] - geometry["root_z"]

    assert geometry["top_z"] == pytest.approx(19.4)
    assert radius_x**2 + radius_z**2 == pytest.approx(5.0**2)
    assert radius_x * side_x + radius_z * side_z == pytest.approx(0.0)


def test_padeye_lug_width_keeps_gusset_below_crown(fusion_generators):
    geometry = fusion_generators._padeye_lug_geometry(
        base_thickness=0.8,
        join_overlap=0.016,
        lug_height=14.0,
        neck_width=8.0,
        root_width=13.64,
    )

    half_width = fusion_generators._padeye_lug_half_width(
        geometry,
        root_width=13.64,
        z=12.8,
    )

    assert half_width > 1.8
    with pytest.raises(RuntimeError, match="terminate below"):
        fusion_generators._padeye_lug_half_width(
            geometry,
            root_width=13.64,
            z=geometry["top_z"],
        )


def test_stabilizer_pressure_selector_excludes_internal_surfaces(
    fusion_generators,
):
    selector = {
        "root_z": 1.8,
        "span": 80.0,
        "root_chord": 50.0,
        "tip_chord": 25.0,
        "sweep": 17.0,
        "outer_surface_ratio": 0.92,
        "z_min": 1.8,
        "z_max": 21.8,
    }
    external_skin = types.SimpleNamespace(
        centroid=_Point(25.0, 3.4, 11.8),
        boundingBox=_BoundingBox((20.0, 3.0, 1.8), (30.0, 3.8, 21.8)),
    )
    internal_surface = types.SimpleNamespace(
        centroid=_Point(25.0, 2.4, 11.8),
        boundingBox=_BoundingBox((20.0, 2.0, 1.8), (30.0, 2.8, 21.8)),
    )

    assert fusion_generators._pressure_surface_face_matches(
        external_skin, selector
    )
    assert not fusion_generators._pressure_surface_face_matches(
        internal_surface, selector
    )


def test_stabilizer_fillet_selects_only_airfoil_root_loop(fusion_generators):
    root_edges = [
        _Edge((index, -3.0, 1.8), (index + 1.0, -2.0, 1.8))
        for index in range(8)
    ]
    flange_edge = _Edge((-3.0, -8.0, 1.8), (53.0, -8.0, 1.8))
    body = types.SimpleNamespace(edges=[*root_edges, flange_edge])

    class FilletInput:
        def addConstantRadiusEdgeSet(self, edges, radius, tangent_chain):
            self.edges = edges
            self.radius = radius
            self.tangent_chain = tangent_chain

    class FilletFeatures:
        def createInput(self):
            self.input = FilletInput()
            return self.input

        def add(self, input_):
            assert input_ is self.input
            self.feature = types.SimpleNamespace(name=None)
            return self.feature

    fillets = FilletFeatures()
    component = types.SimpleNamespace(
        bRepBodies=_BodyCollection([body]),
        features=types.SimpleNamespace(filletFeatures=fillets),
    )

    fusion_generators._add_stabilizer_root_fillet(
        component,
        radius=2.5,
        flange_thickness=1.8,
        root_chord=50.0,
    )

    assert fillets.input.edges == root_edges
    assert fillets.input.radius == 2.5
    assert fillets.input.tangent_chain is False
    assert fillets.feature.name == "Stabilizer fin-to-flange root fillet"


def test_padeye_fillet_selects_both_full_length_lug_roots(fusion_generators):
    negative_root = _Edge((-9.0, -1.0, 1.4), (9.0, -1.0, 1.4))
    positive_root = _Edge((-9.0, 1.0, 1.4), (9.0, 1.0, 1.4))
    split_root = _Edge((-9.0, 1.0, 1.4), (-4.0, 1.0, 1.4))
    plate_perimeter = _Edge((-13.0, -9.0, 1.4), (13.0, -9.0, 1.4))
    body = types.SimpleNamespace(
        edges=[negative_root, positive_root, split_root, plate_perimeter]
    )

    class FilletInput:
        def addConstantRadiusEdgeSet(self, edges, radius, tangent_chain):
            self.edges = edges
            self.radius = radius
            self.tangent_chain = tangent_chain

    class FilletFeatures:
        def __init__(self):
            self.inputs = []
            self.features = []

        def createInput(self):
            input_ = FilletInput()
            self.inputs.append(input_)
            return input_

        def add(self, input_):
            assert input_ is self.inputs[-1]
            feature = types.SimpleNamespace(name=None)
            self.features.append(feature)
            return feature

    fillets = FilletFeatures()
    component = types.SimpleNamespace(
        bRepBodies=_BodyCollection([body]),
        features=types.SimpleNamespace(filletFeatures=fillets),
    )

    fusion_generators._add_padeye_lug_root_fillets(
        component,
        radius=1.5,
        base_thickness=1.4,
        lug_thickness=2.0,
        root_width=18.0,
    )

    assert [input_.edges for input_ in fillets.inputs] == [
        [negative_root],
        [positive_root],
    ]
    assert all(input_.radius == 1.5 for input_ in fillets.inputs)
    assert all(input_.tangent_chain is False for input_ in fillets.inputs)
    assert [feature.name for feature in fillets.features] == [
        "Padeye negative Y lug-root fillet",
        "Padeye positive Y lug-root fillet",
    ]


def test_padeye_fillet_fails_if_clear_root_is_missing(fusion_generators):
    body = types.SimpleNamespace(
        edges=[_Edge((-9.0, 1.0, 1.4), (-4.0, 1.0, 1.4))]
    )
    component = types.SimpleNamespace(
        bRepBodies=_BodyCollection([body]),
    )

    with pytest.raises(RuntimeError, match="full-length negative Y lug-root edge"):
        fusion_generators._add_padeye_lug_root_fillets(
            component,
            radius=1.5,
            base_thickness=1.4,
            lug_thickness=2.0,
            root_width=18.0,
        )


def test_single_solid_contract_rejects_multiple_bodies(fusion_generators):
    component = types.SimpleNamespace(
        bRepBodies=_BodyCollection([object(), object()])
    )

    with pytest.raises(RuntimeError, match="one connected solid body"):
        fusion_generators._require_single_solid(component, "Padeye joins")


def test_bottom_face_selector_excludes_vertical_faces(fusion_generators):
    underside = types.SimpleNamespace(
        boundingBox=_BoundingBox((-13.0, -9.0, 0.0), (13.0, 9.0, 0.0))
    )
    vertical_side = types.SimpleNamespace(
        boundingBox=_BoundingBox((-13.0, -9.0, 0.0), (13.0, -9.0, 1.4))
    )
    selector = {"kind": "bottom_face", "z_max": 0.01}

    assert fusion_generators._face_matches(underside, selector)
    assert not fusion_generators._face_matches(vertical_side, selector)
