#!/usr/bin/env python3

from app.utils.vector_mapper import match_to_standard, get_measurement_categories

def main():
    # Example measurement names from various brands
    test_measurements = [
        "chest width",
        "chest circumference",
        "bust",
        "waist size",
        "waist circumference",
        "hip measurement",
        "hip circumference",
        "inseam length",
        "inside leg",
        "leg length",
        "collar size",
        "neck measurement",
        "sleeve",
        "arm length",
        "shoulder width",
        # Some edge cases
        "chest pocket width",
        "waistband height",
        "random text",
    ]

    print("Demonstrating measurement name standardization:")
    print("-" * 50)
    
    for measurement in test_measurements:
        standard = match_to_standard(measurement)
        print(f"'{measurement}' -> {standard or 'No match'}")
    
    print("\nStandard measurement categories and variations:")
    print("-" * 50)
    
    categories = get_measurement_categories()
    for standard, variations in categories.items():
        print(f"\n{standard.upper()}:")
        for var in variations:
            print(f"  - {var}")

if __name__ == "__main__":
    main() 