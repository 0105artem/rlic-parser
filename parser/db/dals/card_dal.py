from typing import List

from loguru import logger
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.models.models import License
from schemas import card_schema


class CardDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_card(self, card: card_schema.License):
        new_card = License(**card.dict())
        self.db_session.add(new_card)
        try:
            await self.db_session.commit()
        except IntegrityError as ex:
            await self.db_session.rollback()
            logger.warning(f"Card {new_card.license_id} already exists!")

    async def create_cards(self, cards: List[card_schema.License]):
        # new_card = Card(**card.dict())
        stmt = insert(License).values([card.dict() for card in cards]).on_conflict_do_nothing()
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def get_card(self, license_id: str):
        q = await self.db_session.execute(select(License).where(License.license_id == license_id))
        return q.scalars().first()

    async def get_all_cards(self) -> List[License]:
        q = await self.db_session.execute(select(License).order_by(License.id))
        return q.scalars().all()
