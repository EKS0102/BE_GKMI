from sqlalchemy import Column, Integer, String, Date, Text
from database.database import Base


class Jemaat(Base):
    __tablename__ = "jemaat"

    id = Column(Integer, primary_key=True, index=True)
    nama_panggilan = Column(String(100), nullable=False)
    nama_lengkap = Column(String(150), nullable=False)
    jenis_kelamin = Column(String(20), nullable=False)
    tanggal_lahir = Column(Date, nullable=False)
    domisili = Column(Text, nullable=False)
    status_jemaat = Column(String(20), nullable=False)
    status_diakonia = Column(String(10), nullable=False)
    kelompok_ibadah = Column(String(30), nullable=False)