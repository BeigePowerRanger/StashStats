from stashstats import RavelryClient


def test_mvp_models_and_endpoints():
    with RavelryClient() as client:
        print("==================================================")
        print("1. TEST GET YARN DETAILS (GET /yarns/62569.json)")
        print("==================================================")
        yarn_detail = client.get_yarn_details(62569)
        yarn = yarn_detail.yarn
        print(f"Yarn Name        : {yarn.yarn_company_name or 'Independent'} - {yarn.name}")
        print(f"Weight / Length  : {yarn.yarn_weight.name if yarn.yarn_weight else 'N/A'} | {yarn.yardage}y / {yarn.grams}g")
        print(f"Rating           : {yarn.rating_average} ({yarn.rating_count} reviews)")
        print(f"Discontinued     : {yarn.discontinued}")
        print(f"Machine Washable : {yarn.machine_washable}")
        print(f"Texture          : {yarn.texture}")
        print("Fiber Breakdown  :")
        for fiber in yarn.yarn_fibers:
            print(f"  - {fiber.percentage}% {fiber.fiber_type.name} (Animal: {fiber.fiber_type.animal_fiber})")

        print("\n==================================================")
        print("2. TEST REFERENCE DATA: COLOR FAMILIES")
        print("==================================================")
        color_families = client.get_color_families()
        print(f"Total Color Families: {len(color_families)}")
        for cf in color_families[:5]:
            print(f"  - [{cf.id}] {cf.name} (Slug: {cf.permalink})")

        print("\n==================================================")
        print("3. TEST REFERENCE DATA: YARN WEIGHTS")
        print("==================================================")
        yarn_weights = client.get_yarn_weights()
        print(f"Total Yarn Weights: {len(yarn_weights)}")
        for yw in yarn_weights[:5]:
            print(f"  - [{yw.id}] {yw.name} (Ply: {yw.ply}, WPI: {yw.wpi}, Gauge: {yw.min_gauge}-{yw.max_gauge})")

        print("\n==================================================")
        print("4. TEST REFERENCE DATA: FIBER CATEGORIES")
        print("==================================================")
        fiber_cats = client.get_fiber_categories()
        print(f"Total Fiber Categories: {len(fiber_cats)}")
        for fc in fiber_cats[:5]:
            print(f"  - [{fc.id}] {fc.name} (Slug: {fc.permalink})")

        print("\n==================================================")
        print("5. TEST GLOBAL STASH SEARCH (GET /stash/search.json)")
        print("==================================================")
        stash_search = client.search_stash(query="Malabrigo Rios", page_size=3)
        print(f"Total Public Stash Matches: {stash_search.paginator.results}")
        for idx, item in enumerate(stash_search.stashes, 1):
            owner = item.user.username if item.user else "Anonymous"
            pack_desc = item.primary_pack.quantity_description if item.primary_pack else "N/A"
            print(f"  {idx}. [{item.id}] {item.name} ({item.colorway_name}) by @{owner}")
            print(f"     Quantity: {pack_desc}")


if __name__ == "__main__":
    test_mvp_models_and_endpoints()
