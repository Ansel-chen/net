from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple


@dataclass
class MetricSample:
    timestamp: float
    latency_ms: float
    bytes_in: int
    bytes_out: int


class MetricsCollector:
    """Sliding-window metrics aggregator for the TCP server."""

    def __init__(self, window_seconds: int = 60) -> None:
        self.window_seconds = window_seconds
        self._samples: Deque[MetricSample] = deque()
        self._lock = threading.Lock()

    def record(self, latency_ms: float, bytes_in: int, bytes_out: int) -> None:
        now = time.time()
        sample = MetricSample(timestamp=now, latency_ms=latency_ms, bytes_in=bytes_in, bytes_out=bytes_out)
        with self._lock:
            self._samples.append(sample)
            self._trim_locked(now)

    def snapshot(self) -> Dict[str, float]:
        now = time.time()
        with self._lock:
            self._trim_locked(now)
            count = len(self._samples)
            if count == 0:
                return {
                    "window_seconds": self.window_seconds,
                    "sample_count": 0,
                    "latency_ms_avg": 0.0,
                    "latency_ms_max": 0.0,
                    "latency_ms_min": 0.0,
                    "rtt_ms_avg": 0.0,
                    "throughput_kbps": 0.0,
                    "requests_per_sec": 0.0,
                }
            total_latency = sum(s.latency_ms for s in self._samples)
            total_bytes = sum(s.bytes_out for s in self._samples)
            latency_max = max(s.latency_ms for s in self._samples)
            latency_min = min(s.latency_ms for s in self._samples)
            span = max(self._samples[-1].timestamp - self._samples[0].timestamp, 1e-6)
            throughput_kbps = (total_bytes / 1024.0) / span
            rps = count / span
            return {
                "window_seconds": self.window_seconds,
                "sample_count": count,
                "latency_ms_avg": total_latency / count,
                "latency_ms_max": latency_max,
                "latency_ms_min": latency_min,
                "rtt_ms_avg": total_latency / count,
                "throughput_kbps": throughput_kbps,
                "requests_per_sec": rps,
            }

    def _trim_locked(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._samples and self._samples[0].timestamp < cutoff:
            self._samples.popleft()


metrics_collector = MetricsCollector(window_seconds=60)
