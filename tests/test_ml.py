"""
Test script for TerraTwin Analog Discovery Engine
"""
from backend.ml.engine import AnalogDiscoveryEngine

def run_tests():
    engine = AnalogDiscoveryEngine()
    print("=== Testing Moon Analog Search ===")
    res_moon = engine.search_analogs('moon', -85.5, 0.0)
    print("Model:", res_moon["model"])
    print("Features compared:", res_moon["features_compared"])
    print("Features excluded:", res_moon["features_excluded"])
    for r in res_moon["results"][:3]:
        print(f"Rank {r['rank']}: {r['name']} (Score: {r['score']})")
        print(f"   Analog Type: {r['analog_type']}")

    print("\n=== Testing Mars Analog Search ===")
    res_mars = engine.search_analogs('mars', 18.38, 77.58)
    print("Features compared:", res_mars["features_compared"])
    print("Features excluded:", res_mars["features_excluded"])
    for r in res_mars["results"][:3]:
        print(f"Rank {r['rank']}: {r['name']} (Score: {r['score']})")
        print(f"   Analog Type: {r['analog_type']}")

if __name__ == "__main__":
    run_tests()
