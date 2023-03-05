from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LicenseBase(BaseModel):
    license_id: str


class License(LicenseBase):
    ogrn: Optional[str]
    grant_decision: Optional[str]
    state: Optional[str]
    fullname: Optional[str]
    license_organ: Optional[str]
    validity: Optional[str]
    region: Optional[str]
    shortname: Optional[str]
    inn: Optional[str]
    kpp: Optional[str]
    reg_number: Optional[str]
    address: Optional[str]
    suspend_decision: Optional[str]
    renew_decision: Optional[str]
    termination_info: Optional[str]
    revoke_decision: Optional[str]
    officials_information: Optional[str]

    class Config:
        orm_mode = True


class LicenseFromDB(License):
    id: int
    created_at: datetime
