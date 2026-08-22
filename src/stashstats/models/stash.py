from pydantic import BaseModel, Field, model_validator

from stashstats.models.common import Paginator, Photo, YarnCompany
from stashstats.models.user import UserProfile
from stashstats.models.yarn import YarnWeight


class StashStatus(BaseModel):
    """Status classification of a stash item."""

    id: int
    """Status numeric identifier (1=in stash, 2=used up, 3=will trade/sell, 4=gone/sold)."""

    name: str
    """Status label (e.g. 'In stash', 'Used up', 'Will trade')."""


class Pack(BaseModel):
    """Skein allocation and purchase record for a stash or project item."""

    id: int
    """Pack unique record ID."""

    stash_id: int | None = None
    """Associated stash item ID."""

    yarn_id: int | None = None
    """Associated catalog yarn ID."""

    colorway: str | None = None
    """Colorway name or number."""

    dye_lot: str | None = None
    """Dye lot identifier."""

    skeins: float | None = None
    """Number of skeins allocated."""

    total_grams: float | None = None
    """Total weight in grams."""

    total_yards: float | None = None
    """Total length in yards."""

    total_meters: float | None = None
    """Total length in meters."""

    total_ounces: float | None = None
    """Total weight in ounces."""

    grams_per_skein: float | None = None
    """Weight per skein in grams."""

    yards_per_skein: float | None = None
    """Length per skein in yards."""

    meters_per_skein: float | None = None
    """Length per skein in meters."""

    ounces_per_skein: float | None = None
    """Weight per skein in ounces."""

    quantity_description: str | None = None
    """Formatted quantity string (e.g., '7 skeins = 1379.0 yards')."""

    shop_name: str | None = None
    """Retailer or shop where yarn was purchased."""

    purchased_date: str | None = None
    """Date purchased (YYYY-MM-DD) if entered by user."""


class StashYarn(BaseModel):
    """Summary yarn profile embedded within a stash item."""

    id: int
    """Catalog yarn database ID."""

    name: str
    """Commercial yarn line name."""

    permalink: str | None = None
    """URL slug for the yarn."""

    yarn_company_name: str | None = None
    """Manufacturer brand name."""

    yarn_company: YarnCompany | None = None
    """Detailed company information."""

    yarn_weight: YarnWeight | None = None
    """Standard yarn weight classification."""

    grams: float | None = None
    """Standard skein weight in grams."""

    yardage: float | None = None
    """Standard skein yardage."""

    rating_average: float | None = None
    """Community average rating (1.0 - 5.0)."""

    rating_count: int | None = None
    """Total number of community ratings."""

    photos: list[Photo] = Field(default_factory=list)
    """Gallery photos of the commercial yarn."""


class StashItem(BaseModel):
    """The standard Ravelry 'Stash (list)' data model.

    This is the most frequently returned Stash object across the Ravelry API,
    returned by GET /people/{username}/stash/list.json and /stash/search.json.
    """

    id: int
    """Stash item unique database ID."""

    name: str | None = None
    """User-added yarn title or label."""

    permalink: str
    """URL slug for this stash entry."""

    colorway_name: str | None = None
    """Name or number of the colorway."""

    color_family_name: str | None = None
    """Color family grouping (e.g. 'Purple', 'Blue')."""

    dye_lot: str | None = None
    """Dye lot string from ball band."""

    location: str | None = None
    """Physical storage location description."""

    comments_count: int = 0
    """Number of comments on this stash entry."""

    favorites_count: int = 0
    """Number of times favorited by Ravelry users."""

    handspun: bool = False
    """Whether the yarn is handspun fiber."""

    has_photo: bool | None = False
    """Whether user uploaded photos for this stash item."""

    created_at: str | None = None
    """Record creation timestamp string."""

    updated_at: str | None = None
    """Last update timestamp string."""

    tag_names: list[str] = Field(default_factory=list)
    """User tags applied to this stash entry."""

    yarn_weight_name: str | None = None
    """Name of the yarn weight (e.g. 'Worsted', 'Fingering')."""

    long_yarn_weight_name: str | None = None
    """Expanded description of the yarn weight."""

    personal_yarn_weight: YarnWeight | None = None
    """User-specified yarn weight if not linked to a database yarn."""

    stash_status: StashStatus | None = None
    """Active status (e.g. 'In stash', 'Used up')."""

    yarn: StashYarn | None = None
    """Associated commercial yarn profile."""

    primary_pack: Pack | None = None
    """Primary skein and purchase pack."""

    packs: list[Pack] = Field(default_factory=list)
    """Allocated skein and purchase packs."""

    skeins: float | None = None
    """Top-level or computed total skein count."""

    total_yards: float | None = None
    """Top-level or computed total yards."""

    total_grams: float | None = None
    """Top-level or computed total grams."""

    total_meters: float | None = None
    """Top-level or computed total meters."""

    notes: str | None = None
    """Personal notes or usage commentary."""

    first_photo: Photo | None = None
    """Primary photo asset for the stash entry."""

    user: UserProfile | None = None
    """Owner user profile."""

    @model_validator(mode="after")
    def normalize_packs_and_quantities(self) -> "StashItem":
        """Normalize pack collections and fallback quantities directly on ingestion."""
        if not self.packs and self.primary_pack:
            self.packs = [self.primary_pack]

        if self.primary_pack:
            if self.skeins is None and self.primary_pack.skeins is not None:
                self.skeins = self.primary_pack.skeins
            if self.total_yards is None and self.primary_pack.total_yards is not None:
                self.total_yards = self.primary_pack.total_yards
            if self.total_grams is None and self.primary_pack.total_grams is not None:
                self.total_grams = self.primary_pack.total_grams
            if self.total_meters is None and self.primary_pack.total_meters is not None:
                self.total_meters = self.primary_pack.total_meters
            if not self.colorway_name and self.primary_pack.colorway:
                self.colorway_name = self.primary_pack.colorway
            if not self.dye_lot and self.primary_pack.dye_lot:
                self.dye_lot = self.primary_pack.dye_lot
        return self


class StashListResponse(BaseModel):
    """Response envelope returned by GET /people/{username}/stash/list.json."""

    paginator: Paginator
    """Pagination metadata metrics."""

    stash: list[StashItem]
    """List of Stash (list) records on the current page."""


class StashDetailResponse(BaseModel):
    """Payload structure returned by GET /people/{username}/stash/{id}.json."""

    stash: StashItem
    """Detailed stash item record."""


class StashSearchResponse(BaseModel):
    """Payload structure returned by GET /stash/search.json."""

    paginator: Paginator
    """Pagination metrics."""

    stashes: list[StashItem] = Field(default_factory=list)
    """List of matching stash items."""


