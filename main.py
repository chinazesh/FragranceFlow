import os

from perfume import Perfume
from inventory import InventoryManager


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INVENTORY_JSON = os.path.join(DATA_DIR, "inventory.json")


def bootstrap_inventory(manager: InventoryManager) -> None:
    if os.path.exists(INVENTORY_JSON):
        manager.load_from_file(INVENTORY_JSON)
        return

    manager.populate_test_inventory()
    manager.save_to_file(INVENTORY_JSON)


def demo_run() -> None:
    manager = InventoryManager(default_overhead_percent=25.0)
    bootstrap_inventory(manager)

    print("--- Welcome to FragranceFlow ---")

    extras = Perfume("Xerjoff", "Erba Pura", 100, 120_000)
    extras_key = extras.inventory_key()
    if extras_key not in manager.list_inventory():
        manager.add_perfume(extras)
        manager.save_to_file(INVENTORY_JSON)

    print(f"Loaded: {extras}")
    print("\nCurrent inventory:")
    for key in sorted(manager.list_inventory()):
        print(f" • {manager.get_perfume(key)}")

    sample_key = extras.inventory_key()
    decants = manager.calculate_decant_prices(sample_key, overhead_percent=30.0)
    print("\nErba Pura sample decant prices (30% overhead):")
    for size, amount in decants.items():
        print(f" • {size}: {amount}")

    duplicate = Perfume("Xerjoff", "Erba Pura", 100, 120_000)
    try:
        manager.add_perfume(duplicate)
    except ValueError as err:
        print(f"\nExpected duplicate guard: {err}")

    try:
        manager.calculate_decant_prices("Missing - Item")
    except KeyError as err:
        print(f"Expected lookup failure: {err}")


def main() -> None:
    demo_run()


if __name__ == "__main__":
    main()
