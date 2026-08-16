from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Yarn weight name cannot be empty")
        return v_stripped

    @field_validator("ply", "wpi", mode="before")
    @classmethod
    def normalize_str_fields(cls, v: Any) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

    @field_validator("min_gauge", "max_gauge")
    @classmethod
    def validate_gauge_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Gauge values cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_gauge_range(self) -> "YarnWeight":
        if self.min_gauge is not None and self.max_gauge is not None and self.min_gauge > self.max_gauge:
            raise ValueError(
                f"min_gauge ({self.min_gauge}) cannot be greater than max_gauge ({self.max_gauge})"
            )
        return self


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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Fiber type name cannot be empty")
        return v_stripped

    @field_validator("animal_fiber", "synthetic", "vegetable", mode="before")
    @classmethod
    def normalize_bool_flags(cls, v: Any) -> bool:
        if v is None:
            return False
        return bool(v)


class YarnFiber(BaseModel):
    """Fiber composition entry with percentage breakdown."""

    id: int
    """Yarn fiber component ID."""

    percentage: int
    """Percentage of total yarn composition."""

    fiber_type: FiberType
    """Detailed fiber classification."""

    @field_validator("percentage", mode="before")
    @classmethod
    def validate_percentage(cls, v: Any) -> int:
        if v is None:
            raise ValueError("Fiber percentage cannot be None")
        try:
            val = round(float(v))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid fiber percentage: {v}")
        if not (0 <= val <= 100):
            raise ValueError(f"Fiber percentage must be between 0 and 100, got {val}")
        return val


class Colorway(BaseModel):
    """Colorway classification and grouping."""

    id: int
    """Colorway database ID."""

    name: str
    """Name or identifier of colorway."""

    color_family_id: int | None = None
    """Associated color family ID."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Colorway name cannot be empty")
        return v_stripped

    @field_validator("color_family_id")
    @classmethod
    def validate_color_family_id(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("color_family_id cannot be negative")
        return v


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

    @field_validator("name", "permalink")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Field cannot be empty")
        return v_stripped

    @field_validator("grams", "yardage")
    @classmethod
    def validate_non_negative_measurements(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Measurement cannot be negative")
        return v

    @field_validator("rating_average")
    @classmethod
    def validate_rating_average(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 5.0):
            raise ValueError(f"Rating average must be between 0.0 and 5.0, got {v}")
        return v

    @field_validator("rating_count")
    @classmethod
    def validate_rating_count(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Rating count cannot be negative")
        return v

    @field_validator("yarn_fibers", "photos", mode="before")
    @classmethod
    def normalize_list_fields(cls, v: Any) -> list:
        if v is None:
            return []
        return v

    @field_validator("discontinued", mode="before")
    @classmethod
    def normalize_discontinued(cls, v: Any) -> bool:
        if v is None:
            return False
        return bool(v)

    @model_validator(mode="after")
    def sync_company_name(self) -> "Yarn":
        if self.yarn_company and self.yarn_company.name and not self.yarn_company_name:
            self.yarn_company_name = self.yarn_company.name
        return self


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

    @field_validator("name", "permalink")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Field cannot be empty")
        return v_stripped

    @field_validator(
        "grams",
        "yardage",
        "wpi",
        "min_gauge",
        "max_gauge",
        "gauge_divisor",
        "rating_count",
        "rating_total",
    )
    @classmethod
    def validate_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Value cannot be negative")
        return v

    @field_validator("rating_average")
    @classmethod
    def validate_rating_average(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 5.0):
            raise ValueError(f"Rating average must be between 0.0 and 5.0, got {v}")
        return v

    @field_validator("discontinued", mode="before")
    @classmethod
    def normalize_discontinued(cls, v: Any) -> bool:
        if v is None:
            return False
        return bool(v)

    @model_validator(mode="after")
    def validate_gauge_range(self) -> "YarnSearchResult":
        if self.min_gauge is not None and self.max_gauge is not None and self.min_gauge > self.max_gauge:
            raise ValueError(
                f"min_gauge ({self.min_gauge}) cannot be greater than max_gauge ({self.max_gauge})"
            )
        return self


class YarnSearchResponse(BaseModel):
    """Payload structure returned by GET /yarns/search.json."""

    paginator: Paginator
    """Pagination metrics."""

    yarns: list[YarnSearchResult] = Field(default_factory=list)
    """List of matching yarn search results."""

    @field_validator("yarns", mode="before")
    @classmethod
    def normalize_yarns(cls, v: Any) -> list:
        if v is None:
            return []
        return v


class YarnDetailResponse(BaseModel):
    """Payload structure returned by GET /yarns/{id}.json."""

    yarn: Yarn
    """Full yarn detail record."""

