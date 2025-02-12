from pydantic import BaseModel, Field
from typing import Optional

class InstagramParameters(BaseModel):
    """
    Pydantic model for validating Instagram extracted parameters.
    """
    av: Optional[str] = Field(None, description="User ID from the HTML source")
    user_id: Optional[str] = Field(None, alias="__user", description="User ID from the USER_ID field")
    hs_session: Optional[str] = Field(None, alias="__hs", description="Haste session ID")
    connection_class: Optional[str] = Field(None, alias="__ccg", description="Connection class")
    client_revision: Optional[str] = Field(None, alias="__rev", description="Client revision ID")
    comet_request: Optional[str] = Field(None, alias="__comet_req", description="Comet request number")
    jazoest: Optional[str] = Field(None, description="Security validation parameter")
    spin_revision: Optional[str] = Field(None, alias="__spin_r", description="Spin revision")
    spin_bundle: Optional[str] = Field(None, alias="__spin_b", description="Spin bundle ID")
    spin_timestamp: Optional[str] = Field(None, alias="__spin_t", description="Spin timestamp")
    fb_dtsg: Optional[str] = Field(None, description="DTSG security token")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Converts a dictionary into a validated InstagramParameters instance.
        """
        return cls(**data)
