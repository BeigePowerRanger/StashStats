from pydantic import BaseModel


class ColorFamily(BaseModel):
    """Ravelry color family reference classification."""

    id: int
    """Unique color family ID."""

    name: str
    """Color family name (e.g., 'Red', 'Blue', 'Natural/Undyed')."""

    permalink: str
    """URL-safe slug for color family."""

    spectrum_order: int | None = None
    """Spectral sequence index for ordering."""


class YarnWeightReference(BaseModel):
    """Reference yarn weight taxonomy specification."""

    id: int
    """Unique yarn weight taxonomy identifier."""

    name: str
    """Standard weight name (e.g., 'Worsted', 'Fingering')."""

    ply: str | None = None
    """Standard ply description."""

    wpi: str | None = None
    """Wraps per inch specification."""

    min_gauge: float | None = None
    """Minimum recommended stitch gauge."""

    max_gauge: float | None = None
    """Maximum recommended stitch gauge."""

    crochet_gauge: str | None = None
    """Recommended crochet gauge."""


class FiberCategory(BaseModel):
    """Top-level fiber category reference."""

    id: int
    """Unique fiber category ID."""

    name: str
    """Fiber category name (e.g., 'Plant fiber', 'Animal fiber')."""

    permalink: str
    """URL-safe slug for fiber category."""


class ColorFamiliesResponse(BaseModel):
    """Payload structure returned by GET /color_families.json."""

    color_families: list[ColorFamily]


class YarnWeightsResponse(BaseModel):
    """Payload structure returned by GET /yarn_weights.json."""

    yarn_weights: list[YarnWeightReference]


class FiberCategoriesResponse(BaseModel):
    """Payload structure returned by GET /fiber_categories.json."""

    fiber_categories: list[FiberCategory]

