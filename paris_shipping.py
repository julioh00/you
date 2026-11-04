#!/usr/bin/env python3
"""
Paris Shipping Store
====================
A CLI app to manage a parcel shipping store located in Paris.

Features:
- Register packages with sender/recipient details
- 5 destination zones (Paris, Ile-de-France, France, Europe, International)
- 3 service types (Economy, Standard, Express)
- Automatic price calculation (base rate + per-kg + volumetric weight + insurance)
- Unique tracking numbers
- Package status flow: received -> in_transit -> out_for_delivery -> delivered
- Track a package by tracking number
- List packages by status
- Store statistics (revenue, packages per zone/status)
- Save/Load state to a JSON file

Usage:
    python paris_shipping.py [data_file]

Example:
    python paris_shipping.py                  # Uses ./paris_shipping_data.json
    python paris_shipping.py my_store.json    # Uses a custom data file
"""

import json
import os
import secrets
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "paris_shipping_data.json"
)

ZONES = {
    "paris": {"name": "Paris intra-muros (75)", "base": 4.90, "per_kg": 0.90, "days": 1},
    "idf": {"name": "Ile-de-France", "base": 6.50, "per_kg": 1.10, "days": 2},
    "france": {"name": "France metropolitaine", "base": 8.90, "per_kg": 1.40, "days": 3},
    "europe": {"name": "Europe", "base": 14.90, "per_kg": 2.20, "days": 5},
    "world": {"name": "International", "base": 24.90, "per_kg": 3.50, "days": 10},
}

SERVICES = {
    "economy": {"name": "Economy", "multiplier": 0.9, "extra_days": 2},
    "standard": {"name": "Standard", "multiplier": 1.0, "extra_days": 0},
    "express": {"name": "Express", "multiplier": 1.6, "extra_days": -1},
}

STATUS_FLOW = ["received", "in_transit", "out_for_delivery", "delivered"]

STATUS_LABELS = {
    "received": "Received at store",
    "in_transit": "In transit",
    "out_for_delivery": "Out for delivery",
    "delivered": "Delivered",
    "cancelled": "Cancelled",
}

INSURANCE_RATE = 0.02
INSURANCE_MIN = 1.00
VOLUMETRIC_DIVISOR = 5000


def now_str() -> str:
    """Return the current timestamp as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_tracking_number() -> str:
    """Generate a unique tracking number like PRS251104A1B2C3."""
    return "PRS" + datetime.now().strftime("%y%m%d") + secrets.token_hex(3).upper()


class Package:
    """A single parcel registered at the store."""

    def __init__(
        self,
        sender: str,
        recipient: str,
        address: str,
        city: str,
        postal_code: str,
        country: str,
        weight_kg: float,
        zone: str,
        service: str,
        length_cm: Optional[float] = None,
        width_cm: Optional[float] = None,
        height_cm: Optional[float] = None,
        declared_value: float = 0.0,
        tracking_number: Optional[str] = None,
        status: str = "received",
        price: float = 0.0,
        created_at: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ):
        self.tracking_number = tracking_number or generate_tracking_number()
        self.sender = sender
        self.recipient = recipient
        self.address = address
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.weight_kg = weight_kg
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.height_cm = height_cm
        self.zone = zone
        self.service = service
        self.declared_value = declared_value
        self.status = status
        self.price = price
        self.created_at = created_at or now_str()
        self.history = history or [{"timestamp": self.created_at, "status": status}]

    def volumetric_weight(self) -> Optional[float]:
        """Return the volumetric weight in kg if dimensions are known."""
        if self.length_cm and self.width_cm and self.height_cm:
            return (self.length_cm * self.width_cm * self.height_cm) / VOLUMETRIC_DIVISOR
        return None

    def chargeable_weight(self) -> float:
        """Return the weight used for pricing: max(real, volumetric)."""
        volumetric = self.volumetric_weight()
        if volumetric is not None:
            return max(self.weight_kg, volumetric)
        return self.weight_kg

    def estimated_days(self) -> int:
        """Return the estimated delivery time in days."""
        extra = SERVICES[self.service]["extra_days"]
        return max(1, ZONES[self.zone]["days"] + extra)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the package to a dictionary."""
        return {
            "tracking_number": self.tracking_number,
            "sender": self.sender,
            "recipient": self.recipient,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "weight_kg": self.weight_kg,
            "length_cm": self.length_cm,
            "width_cm": self.width_cm,
            "height_cm": self.height_cm,
            "zone": self.zone,
            "service": self.service,
            "declared_value": self.declared_value,
            "status": self.status,
            "price": self.price,
            "created_at": self.created_at,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Package":
        """Rebuild a package from a dictionary."""
        return cls(**data)

    def describe(self) -> str:
        """Return a human-readable summary of the package."""
        lines = [
            f"Tracking number : {self.tracking_number}",
            f"Status          : {STATUS_LABELS.get(self.status, self.status)}",
            f"From            : {self.sender}",
            f"To              : {self.recipient}, {self.address}, {self.postal_code} {self.city}, {self.country}",
            f"Zone            : {ZONES[self.zone]['name'] if self.zone in ZONES else self.zone}",
            f"Service         : {SERVICES[self.service]['name'] if self.service in SERVICES else self.service}",
            f"Weight          : {self.weight_kg:.2f} kg (chargeable: {self.chargeable_weight():.2f} kg)",
            f"Declared value  : {self.declared_value:.2f} EUR",
            f"Price           : {self.price:.2f} EUR",
            f"Estimated       : {self.estimated_days()} day(s)",
            f"Registered      : {self.created_at}",
            "History         :",
        ]
        for entry in self.history:
            lines.append(f"  - {entry['timestamp']} : {STATUS_LABELS.get(entry['status'], entry['status'])}")
        return "\n".join(lines)


class ShippingStore:
    """The shipping store: manages packages and pricing."""

    def __init__(self, data_file: str = DEFAULT_DATA_FILE):
        self.data_file = data_file
        self.packages: Dict[str, Package] = {}
        self.load()

    def calculate_price(self, weight_kg: float, zone: str, service: str,
                        length_cm: Optional[float] = None,
                        width_cm: Optional[float] = None,
                        height_cm: Optional[float] = None,
                        declared_value: float = 0.0) -> Tuple[float, float]:
        """
        Calculate the shipping price.

        Returns:
            Tuple of (chargeable_weight, total_price).
        """
        if zone not in ZONES:
            raise ValueError(f"Unknown zone: {zone}")
        if service not in SERVICES:
            raise ValueError(f"Unknown service: {service}")
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than 0")

        volumetric = None
        if length_cm and width_cm and height_cm:
            volumetric = (length_cm * width_cm * height_cm) / VOLUMETRIC_DIVISOR
        chargeable = max(weight_kg, volumetric) if volumetric is not None else weight_kg

        z = ZONES[zone]
        price = z["base"] + chargeable * z["per_kg"]
        price *= SERVICES[service]["multiplier"]
        if declared_value > 0:
            price += max(INSURANCE_MIN, declared_value * INSURANCE_RATE)
        return chargeable, round(price, 2)

    def register_package(self, sender: str, recipient: str, address: str, city: str,
                         postal_code: str, country: str, weight_kg: float, zone: str,
                         service: str, length_cm: Optional[float] = None,
                         width_cm: Optional[float] = None, height_cm: Optional[float] = None,
                         declared_value: float = 0.0) -> Package:
        """Register a new package and compute its price."""
        _, price = self.calculate_price(
            weight_kg, zone, service, length_cm, width_cm, height_cm, declared_value
        )
        package = Package(
            sender=sender, recipient=recipient, address=address, city=city,
            postal_code=postal_code, country=country, weight_kg=weight_kg,
            zone=zone, service=service, length_cm=length_cm, width_cm=width_cm,
            height_cm=height_cm, declared_value=declared_value, price=price,
        )
        self.packages[package.tracking_number] = package
        self.save()
        return package

    def find(self, tracking_number: str) -> Optional[Package]:
        """Find a package by tracking number (case-insensitive)."""
        return self.packages.get(tracking_number.strip().upper())

    def update_status(self, tracking_number: str, new_status: str) -> Optional[Package]:
        """
        Move a package to the next status in the flow.

        Allowed transitions follow STATUS_FLOW; a package in 'received'
        can also be 'cancelled'. Returns the updated package or None.
        """
        package = self.find(tracking_number)
        if package is None:
            return None
        if new_status == "cancelled" and package.status == "received":
            package.status = new_status
        elif new_status in STATUS_FLOW:
            current_index = STATUS_FLOW.index(package.status) if package.status in STATUS_FLOW else -1
            if STATUS_FLOW.index(new_status) != current_index + 1:
                return None
            package.status = new_status
        else:
            return None
        package.history.append({"timestamp": now_str(), "status": package.status})
        self.save()
        return package

    def list_by_status(self, status: str) -> List[Package]:
        """Return all packages with the given status."""
        return [p for p in self.packages.values() if p.status == status]

    def statistics(self) -> Dict[str, Any]:
        """Compute store statistics."""
        by_status: Dict[str, int] = {}
        by_zone: Dict[str, int] = {}
        total_weight = 0.0
        revenue = 0.0
        for p in self.packages.values():
            by_status[p.status] = by_status.get(p.status, 0) + 1
            by_zone[p.zone] = by_zone.get(p.zone, 0) + 1
            total_weight += p.chargeable_weight()
            revenue += p.price
        return {
            "total_packages": len(self.packages),
            "by_status": by_status,
            "by_zone": by_zone,
            "total_chargeable_weight": round(total_weight, 2),
            "revenue_eur": round(revenue, 2),
        }

    def save(self) -> None:
        """Save all packages to the JSON data file."""
        data = {tn: p.to_dict() for tn, p in self.packages.items()}
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Load packages from the JSON data file if it exists."""
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.packages = {tn: Package.from_dict(d) for tn, d in data.items()}


def print_welcome() -> None:
    """Print the welcome banner."""
    print(r"""
  ____                 _        _____ _     _             _             
 |  _ \ __ _ _ __ ___(_)___   / ____| |   (_)_ __  _ __ (_)_ __  _ __  
 | |_) / _` | '__/ __| / __| | (___ | |__  | | '_ \| '_ \| | '_ \| '_ \ 
 |  __/ (_| | | | (__| \__ \  \___ \| '_ \ | | |_) | |_) | | | | | | | |
 |_|   \__,_|_|  \___|_|___/  ____) | | | | | .__/| .__/|_|_| |_|_| |_|"""
    )
    print("""
    Welcome to the Paris Shipping Store!
    """)


def ask(prompt: str, required: bool = True) -> str:
    """Ask for a text input until a non-empty value is given if required."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required.")


def ask_float(prompt: str, min_value: float = 0.0) -> float:
    """Ask for a positive float."""
    while True:
        try:
            value = float(input(prompt).strip())
            if value > min_value:
                return value
            print(f"Please enter a number greater than {min_value}.")
        except ValueError:
            print("Please enter a valid number.")


def ask_optional_float(prompt: str) -> Optional[float]:
    """Ask for an optional positive float."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            value = float(raw)
            if value > 0:
                return value
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number or leave empty.")


def ask_choice(prompt: str, options: Dict[str, Any]) -> str:
    """Ask the user to pick one of the given options."""
    print(prompt)
    for key, value in options.items():
        label = value["name"] if isinstance(value, dict) and "name" in value else value
        print(f"  {key}. {label}")
    while True:
        choice = input("Choice: ").strip().lower()
        if choice in options:
            return choice
        print(f"Please enter one of: {', '.join(options.keys())}")


def action_register(store: ShippingStore) -> None:
    """Register a new package interactively."""
    print("\n--- Register a new package ---")
    sender = ask("Sender name: ")
    recipient = ask("Recipient name: ")
    address = ask("Recipient address: ")
    city = ask("Recipient city: ")
    postal_code = ask("Recipient postal code: ")
    country = ask("Recipient country: ")
    weight = ask_float("Weight (kg): ")
    zone = ask_choice("Destination zone:", ZONES)
    service = ask_choice("Service type:", SERVICES)
    print("Dimensions (optional, press Enter to skip):")
    length = ask_optional_float("  Length (cm): ")
    width = ask_optional_float("  Width (cm): ")
    height = ask_optional_float("  Height (cm): ")
    if not (length and width and height):
        length = width = height = None
    declared = ask_float("Declared value in EUR (0 for none): ", min_value=-0.001)
    package = store.register_package(
        sender, recipient, address, city, postal_code, country,
        weight, zone, service, length, width, height, max(0.0, declared),
    )
    print(f"\nPackage registered! Tracking number: {package.tracking_number}")
    print(f"Price: {package.price:.2f} EUR | Estimated delivery: {package.estimated_days()} day(s)")
    store.save()


def action_track(store: ShippingStore) -> None:
    """Look up a package by tracking number."""
    print("\n--- Track a package ---")
    tracking = ask("Tracking number: ")
    package = store.find(tracking)
    if package is None:
        print(f"No package found with tracking number '{tracking.upper()}'.")
    else:
        print()
        print(package.describe())


def action_update_status(store: ShippingStore) -> None:
    """Advance a package to its next status."""
    print("\n--- Update package status ---")
    tracking = ask("Tracking number: ")
    package = store.find(tracking)
    if package is None:
        print(f"No package found with tracking number '{tracking.upper()}'.")
        return
    if package.status == "delivered":
        print("This package has already been delivered.")
        return
    if package.status == "cancelled":
        print("This package has been cancelled.")
        return
    if package.status == "received":
        print("Options: 1. Move to 'In transit'  2. Cancel the package")
        choice = input("Choice: ").strip()
        if choice == "2":
            updated = store.update_status(tracking, "cancelled")
        else:
            updated = store.update_status(tracking, "in_transit")
    else:
        updated = store.update_status(
            tracking, STATUS_FLOW[STATUS_FLOW.index(package.status) + 1]
        )
    if updated is None:
        print("Invalid status transition.")
    else:
        print(f"Status updated: {STATUS_LABELS[updated.status]}")


def action_list_by_status(store: ShippingStore) -> None:
    """List packages filtered by status."""
    print("\n--- List packages by status ---")
    options = {s: STATUS_LABELS[s] for s in STATUS_FLOW + ["cancelled"]}
    status = ask_choice("Status:", options)
    packages = store.list_by_status(status)
    if not packages:
        print(f"No packages with status '{STATUS_LABELS[status]}'.")
        return
    for p in packages:
        print(f"  {p.tracking_number} | {p.recipient} | {p.city}, {p.country} | "
              f"{p.price:.2f} EUR | {ZONES[p.zone]['name']}")


def action_list_all(store: ShippingStore) -> None:
    """List every package."""
    print("\n--- All packages ---")
    if not store.packages:
        print("No packages registered yet.")
        return
    for p in sorted(store.packages.values(), key=lambda x: x.created_at):
        print(f"  {p.tracking_number} | {STATUS_LABELS[p.status]:<20} | {p.sender} -> {p.recipient} | {p.price:.2f} EUR")


def action_statistics(store: ShippingStore) -> None:
    """Show store statistics."""
    print("\n--- Store statistics ---")
    stats = store.statistics()
    print(f"Total packages : {stats['total_packages']}")
    print(f"Revenue        : {stats['revenue_eur']:.2f} EUR")
    print(f"Total chargeable weight: {stats['total_chargeable_weight']:.2f} kg")
    print("By status:")
    for status, count in sorted(stats["by_status"].items()):
        print(f"  {STATUS_LABELS.get(status, status):<20}: {count}")
    print("By zone:")
    for zone, count in sorted(stats["by_zone"].items()):
        print(f"  {ZONES[zone]['name'] if zone in ZONES else zone:<28}: {count}")


def main() -> None:
    """Main function: run the interactive store menu."""
    data_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    store = ShippingStore(data_file)
    print_welcome()
    print(f"Data file: {data_file}")

    menu = {
        "1": ("Register a new package", action_register),
        "2": ("Track a package", action_track),
        "3": ("Update package status", action_update_status),
        "4": ("List packages by status", action_list_by_status),
        "5": ("List all packages", action_list_all),
        "6": ("Store statistics", action_statistics),
        "7": ("Save and exit", None),
    }

    while True:
        print("\n===== Main menu =====")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
        choice = input("Choice: ").strip()
        if choice == "7":
            store.save()
            print("Data saved. Goodbye!")
            break
        if choice in menu:
            menu[choice][1](store)
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
