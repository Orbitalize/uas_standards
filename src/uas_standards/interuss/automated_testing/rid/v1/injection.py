"""Data types and operations from Remote ID Test Data Injection 0.0.1 OpenAPI"""

# This file is autogenerated; do not modify manually!

from __future__ import annotations

from enum import Enum
from typing import Dict, List

from uas_standards import Operation

from implicitdict import ImplicitDict


from uas_standards.astm.f3411.v19.api import RIDFlightDetails


class TestFlightDetails(ImplicitDict):
    """The set of data with which the Service Provider system under test should respond when queried for the details of a test flight."""

    effective_after: str
    """The time after which the Service Provider system under test should respond with `details`, unless other `details` with a more recent `effective_after` time (before the current time) are available."""

    details: RIDFlightDetails
    """The details of the flight. Follows the RIDFlightDetails schema from the ASTM remote ID standard."""


from uas_standards.astm.f3411.v19.api import RIDAircraftState


class TestFlight(ImplicitDict):
    """The set of data to be injected into a Service Provider system under test for a single flight."""

    injection_id: str
    """ID of the injected test flight.  Remains the same regardless of the flight ID/UTM ID reported in the system."""

    telemetry: List[RIDAircraftState]
    """The set of telemetry data that should be injected into the system for this flight. Each element follows the RIDAircraftState schema from the ASTM remote ID standard."""

    details_responses: List[TestFlightDetails]
    """The details of the flight as a function of time."""


class CreateTestParameters(ImplicitDict):
    """A complete set of data to be injected into a Service Provider system under test."""

    requested_flights: List[TestFlight]
    """One or more logical flights, each containing test data to inject into the system. Elements should be sorted in ascending order of `timestamp`."""


class ChangeTestResponse(ImplicitDict):
    injected_flights: List[TestFlight]
    """The complete set of test data actually injected into the Service Provider system under test."""

    version: str
    """Version of test.  Used to delete test."""


class DeleteTestResponse(ImplicitDict):
    injected_flights: List[TestFlight]
    """The complete set of test data deleted."""


class OperationID(str, Enum):
    CreateTest = "createTest"
    DeleteTest = "deleteTest"


OPERATIONS: Dict[OperationID, Operation] = {
    OperationID.CreateTest: Operation(
        id="createTest",
        path="/tests/{test_id}",
        verb="PUT",
        request_body_type=CreateTestParameters,
        response_body_type={
            200: ChangeTestResponse,
            409: None,
        }
    ),
    OperationID.DeleteTest: Operation(
        id="deleteTest",
        path="/tests/{test_id}/{version}",
        verb="DELETE",
        request_body_type=None,
        response_body_type={
            200: DeleteTestResponse,
        }
    ),
}
