# flake8: noqa: E800
from math import inf
from typing import Optional

from opentelemetry.sdk.metrics._internal.point import HistogramDataPoint
from opentelemetry.sdk.metrics._internal.aggregation import _DataPointVarT
from opentelemetry.sdk.metrics._internal.aggregation import (
    AggregationTemporality, _ExplicitBucketHistogramAggregation)


def collect(
    self,
    collection_aggregation_temporality: AggregationTemporality,
    collection_start_nano: int,
) -> Optional[_DataPointVarT]:
    """Patched to work around open-telemetry/opentelemetry-python#3089"""

    with self._lock:
        # if not any(self._bucket_counts):  # patched
        #     return None

        bucket_counts = self._bucket_counts
        start_time_unix_nano = self._start_time_unix_nano
        sum_ = self._sum
        max_ = self._max
        min_ = self._min

        self._bucket_counts = self._get_empty_bucket_counts()
        self._start_time_unix_nano = collection_start_nano
        self._sum = 0
        self._min = inf
        self._max = -inf

    current_point = HistogramDataPoint(
        attributes=self._attributes,
        start_time_unix_nano=start_time_unix_nano,
        time_unix_nano=collection_start_nano,
        count=sum(bucket_counts),
        sum=sum_,
        bucket_counts=tuple(bucket_counts),
        explicit_bounds=self._boundaries,
        min=min_,
        max=max_,
    )

    if not any(bucket_counts):  # patched
        self._previous_point = None
        return current_point

    if self._previous_point is None or (
        self._instrument_aggregation_temporality
        is collection_aggregation_temporality
    ):
        self._previous_point = current_point
        return current_point

    max_ = current_point.max
    min_ = current_point.min

    if (
        collection_aggregation_temporality
        is AggregationTemporality.CUMULATIVE
    ):
        start_time_unix_nano = self._previous_point.start_time_unix_nano
        sum_ = current_point.sum + self._previous_point.sum
        # Only update min/max on delta -> cumulative
        max_ = max(current_point.max, self._previous_point.max)
        min_ = min(current_point.min, self._previous_point.min)
        bucket_counts = [
            curr_count + prev_count
            for curr_count, prev_count in zip(
                current_point.bucket_counts,
                self._previous_point.bucket_counts,
            )
        ]
    else:
        start_time_unix_nano = self._previous_point.time_unix_nano
        sum_ = current_point.sum - self._previous_point.sum
        bucket_counts = [
            curr_count - prev_count
            for curr_count, prev_count in zip(
                current_point.bucket_counts,
                self._previous_point.bucket_counts,
            )
        ]

    current_point = HistogramDataPoint(
        attributes=self._attributes,
        start_time_unix_nano=start_time_unix_nano,
        time_unix_nano=current_point.time_unix_nano,
        count=sum(bucket_counts),
        sum=sum_,
        bucket_counts=tuple(bucket_counts),
        explicit_bounds=current_point.explicit_bounds,
        min=min_,
        max=max_,
    )
    self._previous_point = current_point
    return current_point

_ExplicitBucketHistogramAggregation.collect = collect
