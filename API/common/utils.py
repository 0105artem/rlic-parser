import os
from datetime import datetime
from typing import List
import zipfile


import aiofiles
from aiocsv import AsyncWriter
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_hash(password: str) -> str:
    return pwd_context.hash(password)


async def verify(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def current_date(date_format: str = "%d-%m-%Y_%H.%M.%S") -> str:
    """Return current date and time as string."""
    dt_string = datetime.now().strftime(date_format)
    return dt_string


async def write_csv(csv_filepath: str, header: List[str], values: List[list]) -> None:
    async with aiofiles.open(csv_filepath, "w") as f:
        writer = AsyncWriter(f)
        await writer.writerow(header)
        await writer.writerows(values)


async def create_csv(header: List[str], values: List[list], csv_name: str = None) -> None:
    if csv_name is None:
        csv_name = f"active_licenses_{current_date()}.csv"

    filepath = f"./files/csv/{csv_name}"

    if csv_name[-4:] == '.csv':
        await write_csv(filepath, header, values)
    elif csv_name[-4:] == '.zip':
        csv_filepath = filepath.replace('.zip', '.csv')
        await write_csv(csv_filepath, header, values)
        with zipfile.ZipFile(filepath, mode="w") as archive:
            archive.write(csv_filepath, compress_type=zipfile.ZIP_DEFLATED)
            os.remove(csv_filepath)
