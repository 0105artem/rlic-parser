from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from db.config import Base


class Card(Base):
    __tablename__ = 'cards_oop'

    id = Column(Integer, primary_key=True, nullable=False)
    card_id = Column(String, nullable=False, unique=True)
    ogrn = Column(String, nullable=True)
    grant_decision = Column(String, nullable=True)
    state = Column(String, nullable=True)
    fullname = Column(String, nullable=True)
    license_organ = Column(String, nullable=True)
    validity = Column(String, nullable=True)
    region = Column(String, nullable=True)
    shortname = Column(String, nullable=True)
    inn = Column(String, nullable=True)
    kpp = Column(String, nullable=True)
    reg_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    suspend_decision = Column(String, nullable=True)
    renew_decision = Column(String, nullable=True)
    termination_info = Column(String, nullable=True)
    revoke_decision = Column(String, nullable=True)
    officials_information = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class DBCardFields:
    """Contains card's rus fields and their eng translations."""
    keys = {
        'ОГРН': 'ogrn',
        'Решение о предоставлении': 'grant_decision',
        'Текущий статус лицензии': 'state',
        'Полное наименование организации (ФИО индивидуального предпринимателя)': 'fullname',
        'Наименование органа, выдавшего лицензию': 'license_organ',
        'Срок действия': 'validity',
        'Субьект РФ': 'region',  # Typo in 'Субъект' left on purpose. That's how it's written on the website.
        'Сокращенное наименование организации': 'shortname',
        'ИНН': 'inn',
        'КПП': 'kpp',
        'Регистрационный номер лицензии': 'reg_number',
        'Место нахождения организации': 'address',
        'Решения лицензирующего органа о приостановлении действия': 'suspend_decision',
        'Решения лицензирующего органа о возобновлении действия': 'renew_decision',
        'Основание и дата прекращения действия': 'termination_info',
        'Решения суда об аннулировании лицензии': 'revoke_decision',
        'Информация о должностном лице': 'officials_information'
    }
