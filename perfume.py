from __future__ import annotations

from typing import Any, Mapping


class Perfume:
    """Represents a single bottle in the FragranceFlow inventory."""

    def __init__(
        self,
        brand: str,
        name: str,
        volume_ml: float,
        purchase_price: float,
    ) -> None:
        self.brand = (brand or "").strip()
        self.name = (name or "").strip()
        if not self.brand:
            raise ValueError("Brand cannot be empty.")
        if not self.name:
            raise ValueError("Name cannot be empty.")
        self._volume_ml = self._normalize_volume(volume_ml)
        self.purchase_price = self._normalize_price(purchase_price)

    @property
    def volume_ml(self) -> float:
        return self._volume_ml

    @volume_ml.setter
    def volume_ml(self, value: float) -> None:
        self._volume_ml = self._normalize_volume(value)

    @staticmethod
    def _normalize_volume(value: Any) -> float:
        """Validate bottle volume at construction and updates."""
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Volume must be a numeric value (e.g. 50, 75.5)."
            ) from exc
        if parsed <= 0:
            raise ValueError("Volume must be greater than zero.")
        return parsed

    @staticmethod
    def _normalize_price(value: Any) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Purchase price must be a numeric value.") from exc
        if parsed < 0:
            raise ValueError("Purchase price cannot be negative.")
        return parsed

    @property
    def price_per_ml(self) -> float:
        """Cost per ml derived from total bottle purchase price and volume."""
        return self.purchase_price / self.volume_ml

    def inventory_key(self) -> str:
        """Stable dictionary key matching the project's 'Brand - Name' convention."""
        return f"{self.brand} - {self.name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "brand": self.brand,
            "name": self.name,
            "volume_ml": self.volume_ml,
            "purchase_price": self.purchase_price,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Perfume:
        return cls(
            brand=str(data["brand"]),
            name=str(data["name"]),
            volume_ml=data["volume_ml"],
            purchase_price=data["purchase_price"],
        )

    def __repr__(self) -> str:
        return (
            f"Perfume(brand={self.brand!r}, name={self.name!r}, "
            f"volume_ml={self.volume_ml!r}, purchase_price={self.purchase_price!r})"
        )

    def __str__(self) -> str:
        return f"{self.brand} - {self.name} ({self.volume_ml}ml)"
