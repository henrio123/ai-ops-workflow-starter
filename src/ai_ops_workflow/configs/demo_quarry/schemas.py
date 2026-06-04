"""demo_quarry extraction schema (Phase 0 placeholder).

Defines the domain's extraction target as a Pydantic v2 model. The extractor
asks the LLM to fill this shape and then validates. All fields are synthetic
demo concepts.

Planned model (illustrative, implemented in Phase 1):

    class AggregateOrderFields(BaseModel):
        customer_name: str
        material: str                  # e.g. "0-16 crushed gravel"
        volume_tonnes: float = Field(gt=0)
        delivery_distance_km: float = Field(ge=0)
        delivery_date: date | None = None
        new_customer: bool = False

No logic in Phase 0.
"""
