import importlib.util
import sys
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT / "django" / "GWS" / "reconstruct" / "reconstruct_points.py"
)


def _decorator_factory(*args, **kwargs):
    def _decorator(func):
        return func

    return _decorator


def _load_reconstruct_points_module():
    fake_pygplates = types.ModuleType("pygplates")
    fake_pygplates.InvalidLatLonError = type("InvalidLatLonError", (Exception,), {})
    fake_pygplates.PartitionProperty = types.SimpleNamespace(
        reconstruction_plate_id=object(), valid_time_period=object()
    )
    fake_pygplates.reconstruct = lambda *args, **kwargs: None
    fake_pygplates.reverse_reconstruct = lambda *args, **kwargs: None

    fake_django = types.ModuleType("django")
    fake_django_conf = types.ModuleType("django.conf")
    fake_django_conf.settings = types.SimpleNamespace(THROTTLE=False)
    fake_django_http = types.ModuleType("django.http")
    fake_django_http.HttpResponseBadRequest = type(
        "HttpResponseBadRequest", (Exception,), {}
    )
    fake_django_views = types.ModuleType("django.views")
    fake_django_views_decorators = types.ModuleType("django.views.decorators")
    fake_django_views_csrf = types.ModuleType("django.views.decorators.csrf")
    fake_django_views_csrf.csrf_exempt = _decorator_factory

    fake_rest_framework = types.ModuleType("rest_framework")
    fake_rest_framework_decorators = types.ModuleType("rest_framework.decorators")
    fake_rest_framework_decorators.api_view = _decorator_factory
    fake_rest_framework_decorators.schema = _decorator_factory
    fake_rest_framework_decorators.throttle_classes = _decorator_factory
    fake_rest_framework_throttling = types.ModuleType("rest_framework.throttling")
    fake_rest_framework_throttling.AnonRateThrottle = object

    fake_openapi = types.ModuleType("openapi_schema")
    fake_openapi_schema = types.ModuleType("openapi_schema.reconstruct_points_schema")
    fake_openapi_schema.ReconPointsSchema = type("ReconPointsSchema", (), {})

    fake_utils = types.ModuleType("utils")
    fake_access_control = types.ModuleType("utils.access_control")
    fake_access_control.get_client_ip = lambda request: "127.0.0.1"
    fake_decorators = types.ModuleType("utils.decorators")
    fake_decorators.extract_model_and_times = _decorator_factory
    fake_decorators.extract_params = _decorator_factory
    fake_decorators.return_HttpResponse = _decorator_factory
    fake_parameter_helper = types.ModuleType("utils.parameter_helper")
    fake_parameter_helper.get_anchor_plate_id = lambda params: 0
    fake_parameter_helper.get_bool = lambda params, name, default=False: default
    fake_parameter_helper.get_int = lambda params, name, default=None: default
    fake_parameter_helper.get_lats_lons = lambda params: ([], [])
    fake_parameter_helper.get_value_list = lambda params, name, cast: []
    fake_plate_model_utils = types.ModuleType("utils.plate_model_utils")
    fake_plate_model_utils.UnrecognizedModel = type(
        "UnrecognizedModel", (Exception,), {}
    )
    fake_plate_model_utils.get_rotation_model = lambda model: None
    fake_plate_model_utils.get_static_polygons = lambda model: None
    fake_round_float = types.ModuleType("utils.round_float")
    fake_round_float.round_floats = lambda value: value

    fake_modules = {
        "pygplates": fake_pygplates,
        "django": fake_django,
        "django.conf": fake_django_conf,
        "django.http": fake_django_http,
        "django.views": fake_django_views,
        "django.views.decorators": fake_django_views_decorators,
        "django.views.decorators.csrf": fake_django_views_csrf,
        "rest_framework": fake_rest_framework,
        "rest_framework.decorators": fake_rest_framework_decorators,
        "rest_framework.throttling": fake_rest_framework_throttling,
        "openapi_schema": fake_openapi,
        "openapi_schema.reconstruct_points_schema": fake_openapi_schema,
        "utils": fake_utils,
        "utils.access_control": fake_access_control,
        "utils.decorators": fake_decorators,
        "utils.parameter_helper": fake_parameter_helper,
        "utils.plate_model_utils": fake_plate_model_utils,
        "utils.round_float": fake_round_float,
    }

    previous_modules = {
        name: sys.modules.get(name) for name in fake_modules if name in sys.modules
    }
    sys.modules.update(fake_modules)
    try:
        spec = importlib.util.spec_from_file_location(
            "reconstruct_points_under_test", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        for name in fake_modules:
            if name in previous_modules:
                sys.modules[name] = previous_modules[name]
            else:
                sys.modules.pop(name, None)


class FakeGeometry:
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

    def to_lat_lon(self):
        return self._lat, self._lon


class FakeReconstructedFeatureGeometry:
    def __init__(self, feature, lat, lon):
        self._feature = feature
        self._geometry = FakeGeometry(lat, lon)

    def get_feature(self):
        return self._feature

    def get_reconstructed_geometry(self):
        return self._geometry


class FakeFeature:
    def __init__(self, name, pid=None, valid_time=(None, None), geometry=(0.0, 0.0)):
        self._name = name
        self._pid = pid
        self._valid_time = valid_time
        self._geometry = geometry

    def get_name(self):
        return self._name

    def get_reconstruction_plate_id(self):
        return self._pid

    def get_valid_time(self):
        return self._valid_time

    def get_geometry(self):
        return FakeGeometry(*self._geometry)

    def set_geometry(self, geometry):
        self._geometry = geometry


class ReconstructPointsUnitTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reconstruct_points = _load_reconstruct_points_module()

    def test_reconstruct_skips_unassigned_points(self):
        features = [
            FakeFeature("0", pid=None, valid_time=(None, None), geometry=(36.892, 3.975)),
            FakeFeature("1", pid=101, valid_time=(500, 0), geometry=(39.444, 8.418)),
        ]

        def fake_reconstruct(assigned_point_features, rotation_model, output, timef, anchor_plate_id=0):
            output.extend(
                [
                    FakeReconstructedFeatureGeometry(
                        assigned_point_features[0], 36.892, 3.975
                    ),
                    FakeReconstructedFeatureGeometry(
                        assigned_point_features[1], -25.3722, -55.8914
                    ),
                ]
            )

        self.reconstruct_points.pygplates.reconstruct = fake_reconstruct

        lons, lats, pids, btimes, etimes = self.reconstruct_points._reconstruct(
            features, rotation_model=object(), timef=463.8, anchor_plate_id=0
        )

        self.assertEqual(lons, [None, -55.8914])
        self.assertEqual(lats, [None, -25.3722])
        self.assertEqual(pids, [None, 101])
        self.assertEqual(btimes, [None, 500])
        self.assertEqual(etimes, [None, 0])

    def test_reconstruct_keeps_assigned_points_even_if_unchanged(self):
        features = [FakeFeature("0", pid=701, valid_time=(140, 0), geometry=(54.0, 95.0))]

        def fake_reconstruct(assigned_point_features, rotation_model, output, timef, anchor_plate_id=0):
            output.append(
                FakeReconstructedFeatureGeometry(
                    assigned_point_features[0], 54.0, 95.0
                )
            )

        self.reconstruct_points.pygplates.reconstruct = fake_reconstruct

        lons, lats, *_ = self.reconstruct_points._reconstruct(
            features, rotation_model=object(), timef=140.0, anchor_plate_id=0
        )

        self.assertEqual(lons, [95.0])
        self.assertEqual(lats, [54.0])

    def test_reverse_reconstruct_skips_unassigned_points(self):
        features = [
            FakeFeature("0", pid=None, valid_time=(None, None), geometry=(36.892, 3.975)),
            FakeFeature("1", pid=101, valid_time=(500, 0), geometry=(39.444, 8.418)),
        ]

        self.reconstruct_points.pygplates.reverse_reconstruct = lambda *args, **kwargs: None

        lons, lats, pids, btimes, etimes = self.reconstruct_points._reverse_reconstruct(
            features,
            rotation_model=object(),
            timef=463.8,
            anchor_plate_id=0,
            user_provide_pids_flag=False,
        )

        self.assertEqual(lons, [None, 8.418])
        self.assertEqual(lats, [None, 39.444])
        self.assertEqual(pids, [None, 101])
        self.assertEqual(btimes, [None, 500])
        self.assertEqual(etimes, [None, 0])


if __name__ == "__main__":
    unittest.main()
