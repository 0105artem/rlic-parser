from typing import List

from fastapi import status, HTTPException, Depends, APIRouter, Query, Path, BackgroundTasks

from common.utils import create_csv, current_date
from db.dals.license_dal import LicenseDAL
from db.dals.statistics_dal import StatisticsDAL
from db.dependencies import get_license_dal, get_statistics_dal
from schemas import license_schema
from settings import env

router = APIRouter(
    prefix="/licenses"
)


@router.get("/", response_model=List[license_schema.LicenseFromDB], tags=['Get Licenses'])
async def get_licenses(limit: int = Query(default=100, le=1000, ge=0, description="Количество получаемых лицензий"),
                       skip: int = Query(default=0, ge=0,
                                         description="Количество пропускаемых лицензий с начала списка"),
                       license_dal: LicenseDAL = Depends(get_license_dal)):
    return await license_dal.get_all_licenses(limit, skip)


async def csv_bg_task(num_results, license_dal, csv_filename):
    # Creating csv file with all licenses
    licenses = []
    for i in range(0, num_results - 1000, 1000):
        offset = i
        limit = 1000
        chunk = await license_dal.get_all_licenses(limit=limit, offset=offset)
        licenses += chunk

    header = list(licenses[0].__dict__.keys())[1:]
    values = [list(license.__dict__.values())[1:] for license in licenses]

    await create_csv(header, values, csv_filename)


@router.get("/csv/", tags=["Get CSV"])
async def get_csv(bg_tasks: BackgroundTasks, license_dal: LicenseDAL = Depends(get_license_dal),
                  statistics_dal: StatisticsDAL = Depends(get_statistics_dal)):
    latest_parsing = await statistics_dal.get_latest_parsing(table='active_licenses')
    if latest_parsing:
        csv_filename = latest_parsing.csv_file
        if csv_filename is None:
            csv_filename = f"active_licenses_{current_date()}.zip"
            bg_tasks.add_task(csv_bg_task, latest_parsing.num_results, license_dal, csv_filename)
            await statistics_dal.set_csv_file(task_id=latest_parsing.task_id, csv_filename=csv_filename)
            return {"msg": "CSV file will be available at the link shortly.",
                    "url": f"{env.HOSTNAME}/files/csv/{csv_filename}"}
        else:
            return {"url": f"{env.HOSTNAME}/files/csv/{csv_filename}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Information about successful parsing was not found")


@router.get("/{license_id}/", response_model=license_schema.LicenseFromDB, tags=["Get License By Id"])
async def get_license_by_id(license_id: str = Path(description="Уникальный идентификатор лицензии"),
                   license_dal: LicenseDAL = Depends(get_license_dal)):
    license = await license_dal.get_license(license_id)
    if not license:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"License with license_id {license_id} was not found")
    return license
