from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    character_favorites: Mapped[list["Character"]] = relationship(secondary="favorites_characters", back_populates="favorited_by")
    location_favorites: Mapped[list["Location"]] = relationship(secondary="favorites_locations", back_populates="favorited_by")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "character_favorites": [fav.serialize() for fav in self.character_favorites],
            "location_favorites": [fav.serialize() for fav in self.location_favorites]
            
        }




class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    occupation: Mapped[str] = mapped_column(nullable=False)
    favorited_by: Mapped[list["User"]] = relationship(secondary="favorites_characters", back_populates="character_favorites")


    def serialize(self):
            return {
                "id": self.id,
                "name": self.name,
                "occupation": self.occupation,
                
                
            }



favorites_characters = Table(
    "favorites_characters",
    db.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("character_id", ForeignKey("character.id"))
)





class Location(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(nullable=False)
    favorited_by: Mapped[list["User"]] = relationship(secondary="favorites_locations", back_populates="location_favorites")
   

    def serialize(self):
            return {
                "id": self.id,
                "name": self.name,
                "image": self.image
                
            }



favorites_locations = Table(
    "favorites_locations",
    db.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("location_id", ForeignKey("location.id"))
)