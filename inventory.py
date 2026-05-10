from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, Mapping, Optional

from perfume import Perfume


class InventoryManager:
    """
    In-memory catalogue keyed by 'Brand - Name', with JSON persistence
    and decant price estimates based on cost per ml plus overhead.
    """

    def __init__(self, default_overhead_percent: float = 25.0) -> None:
        self._items: Dict[str, Perfume] = {}
        self.default_overhead_percent = self._normalize_overhead(default_overhead_percent)

    @staticmethod
    def _normalize_overhead(value: Any) -> float:
        try:
            overhead = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Overhead percentage must be numeric.") from exc
        if overhead < 0:
            raise ValueError("Overhead percentage cannot be negative.")
        return overhead

    @staticmethod
    def _normalize_decant_volume_ml(value: Any) -> float:
        try:
            ml = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Decant volume must be a numeric value.") from exc
        if ml <= 0:
            raise ValueError("Decant volume must be greater than zero.")
        return ml

    def add_perfume(self, perfume: Perfume) -> str:
        key = perfume.inventory_key()
        if key in self._items:
            raise ValueError(f"Perfume with key '{key}' is already in inventory.")
        self._items[key] = perfume
        return key

    def remove_perfume(self, key: str) -> Perfume:
        if key not in self._items:
            raise KeyError(f"No perfume found for key '{key}'.")
        return self._items.pop(key)

    def list_inventory(self) -> Dict[str, Perfume]:
        """Return a shallow copy of the underlying dictionary."""
        return dict(self._items)

    def get_perfume(self, key: str) -> Optional[Perfume]:
        return self._items.get(key)

    def calculate_decant_prices(
        self,
        key: str,
        decant_volumes_ml: Iterable[float] = (5, 10),
        overhead_percent: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Selling price for each decant size = ml * price_per_ml * (1 + overhead/100).

        price_per_ml is derived from the bottle's total purchase_price / volume_ml.
        """
        perfume = self._items.get(key)
        if perfume is None:
            raise KeyError(f"No perfume found for key '{key}'.")

        overhead = self.default_overhead_percent
        if overhead_percent is not None:
            overhead = self._normalize_overhead(overhead_percent)

        base_per_ml = perfume.price_per_ml
        multiplier = 1.0 + overhead / 100.0
        prices: Dict[str, float] = {}
        for raw_ml in decant_volumes_ml:
            ml = self._normalize_decant_volume_ml(raw_ml)
            label = f"{ml:g}ml" if ml == int(ml) else f"{ml}ml"
            prices[label] = round(ml * base_per_ml * multiplier, 2)
        return prices

    def save_to_file(self, filepath: str) -> None:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        payload = {key: perfume.to_dict() for key, perfume in self._items.items()}
        with open(filepath, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    def load_from_file(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Inventory file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError("Inventory file must contain a JSON object.")

        loaded: Dict[str, Perfume] = {}
        for key, value in raw.items():
            if not isinstance(value, dict):
                raise ValueError(f"Invalid entry for key '{key}'.")
            perfume = Perfume.from_dict(value)
            derived_key = perfume.inventory_key()
            if derived_key != key:
                raise ValueError(
                    f"Key mismatch for '{key}': data describes '{derived_key}'."
                )
            loaded[key] = perfume
        self._items = loaded

    def populate_test_inventory(self) -> None:
        """Seed data for verifying dictionary lookups and serialization."""
        samples = [
            Perfume("Tom Ford", "Lost Cherry", 50, 150_000),
            Perfume("Jean Paul Gaultier", "Ultra Male", 125, 80_000),
            Perfume("Maison Margiela", "Replica Lazy Sunday Morning", 100, 95_000),
        ]
        for perfume in samples:
            self.add_perfume(perfume)
