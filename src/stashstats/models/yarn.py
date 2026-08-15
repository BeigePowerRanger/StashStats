from pydantic import BaseModel, Field

from stashstats.models.common import Paginator, PersonalAttributes, Photo, YarnCompany


class YarnWeight(BaseModel):
    """Standardized yarn weight classification."""

    id: int
    """Unique yarn weight taxonomy ID."""

    name: str
    """Standard name (e.g., 'Worsted', 'Fingering')."""

    ply: str | None = None
    """Ply description (e.g., '10')."""

    wpi: str | None = None
    """Wraps per inch specification."""

    knit_gauge: str | None = None
    """Recommended knitting gauge."""

    crochet_gauge: str | None = None
    """Recommended crochet gauge."""

    min_gauge: float | None = None
    """Minimum gauge value."""

    max_gauge: float | None = None
    """Maximum gauge value."""


class FiberType(BaseModel):
    """Fiber material classification."""

    id: int
    """Unique fiber type database ID."""

    name: str
    """Fiber type name (e.g., 'Wool', 'Cotton', 'Nylon')."""

    animal_fiber: bool = False
    """Whether fiber is derived from an animal source."""

    synthetic: bool = False
    """Whether fiber is synthetic/man-made."""

    vegetable: bool = False
    """Whether fiber is plant/vegetable derived."""


class YarnFiber(BaseModel):
    """Fiber composition entry with percentage breakdown."""

    id: int
    """Yarn fiber component ID."""

    percentage: int
    """Percentage of total yarn composition."""

    fiber_type: FiberType
    """Detailed fiber classification."""


class Colorway(BaseModel):
    """Colorway classification and grouping."""

    id: int
    """Colorway database ID."""

    name: str
    """Name or identifier of colorway."""

    color_family_id: int | None = None
    """Associated color family ID."""


class Yarn(BaseModel):
    """Full yarn profile and catalog specifications."""

    id: int
    """Ravelry database yarn ID."""

    name: str
    """Commercial yarn line name."""

    permalink: str
    """URL-safe slug for the yarn."""

    yarn_company_name: str | None = None
    """Manufacturer or indie dyer company name."""

    yarn_company: YarnCompany | None = None
    """Detailed manufacturer or dyer information."""

    yarn_weight: YarnWeight | None = None
    """Standard yarn weight classification."""

    grams: float | None = None
    """Standard skein weight in grams."""

    yardage: float | None = None
    """Standard skein length in yards."""

    rating_average: float | None = None
    """Community average rating (1.0 - 5.0)."""

    rating_count: int | None = None
    """Number of community ratings submitted."""

    discontinued: bool = False
    """Whether yarn production has ceased."""

    machine_washable: bool | None = None
    """Machine washability care instruction flag."""

    texture: str | None = None
    """Yarn construction texture (e.g. 'plied', 'singles')."""

    gauge_description: str | None = None
    """Human-readable gauge description string."""

    yarn_fibers: list[YarnFiber] = Field(default_factory=list)
    """Fiber composition percentage breakdown."""

    photos: list[Photo] = Field(default_factory=list)
    """Gallery photos of the commercial yarn."""



class YarnSearchResult(BaseModel):
    """Summary yarn record returned in search queries."""

    id: int
    """Ravelry database yarn ID."""

    name: str
    """Commercial yarn line name."""

    permalink: str
    """URL-safe slug for the yarn."""

    yarn_company_name: str | None = None
    """Manufacturer or indie dyer company name."""

    grams: float | None = None
    """Standard skein weight in grams."""

    yardage: float | None = None
    """Standard skein length in yards."""

    discontinued: bool = False
    """Whether production has ceased."""

    machine_washable: bool | None = None
    """Care instruction flag."""

    texture: str | None = None
    """Yarn construction texture (e.g. 'plied', 'singles')."""

    wpi: int | None = None
    """Wraps per inch."""

    min_gauge: float | None = None
    """Minimum recommended gauge."""

    max_gauge: float | None = None
    """Maximum recommended gauge."""

    gauge_divisor: int | None = None
    """Gauge span in inches (typically 4)."""

    rating_average: float | None = None
    """Community average rating (1.0 - 5.0)."""

    rating_count: int | None = None
    """Number of ratings submitted."""

    rating_total: int | None = None
    """Sum of all rating values."""

    first_photo: Photo | None = None
    """Primary representative photo asset."""

    yarn_weight: YarnWeight | None = None
    """Weight classification specifications."""

    personal_attributes: PersonalAttributes | None = None
    """Authenticated user interaction state if requested."""


class YarnSearchResponse(BaseModel):
    """Payload structure returned by GET /yarns/search.json."""

    paginator: Paginator
    """Pagination metrics."""

    yarns: list[YarnSearchResult]
    """List of matching yarn search results."""


class YarnDetailResponse(BaseModel):
    """Payload structure returned by GET /yarns/{id}.json."""

    yarn: Yarn
    """Full yarn detail record."""

