# ==========================================
# SQLALCHEMY MODELS (Zone 2 of ERD)
# ==========================================

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base # Import Base from your core config

class User(Base):
    __tablename__ = "Users"
    User_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    First_Name = Column(String, nullable=False)
    Last_Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False, index=True)
    Phone_Number = Column(String)
    Hashed_Password = Column(String, nullable=True)

    # Relationship back to Bookings
    bookings = relationship("Booking", back_populates="user")

class Booking(Base):
    __tablename__ = "Bookings"
    Booking_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    User_Id = Column(Integer, ForeignKey("Users.User_ID"), nullable=False)
    Agent_Id = Column(Integer, nullable=True) # Assuming Agents table is separate
    Start_Date = Column(Date, nullable=False)
    End_Date = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    hotel_reservations = relationship("HotelReservation", back_populates="booking", cascade="all, delete-orphan")
    flight_reservations = relationship("FlightReservation", back_populates="booking", cascade="all, delete-orphan")
    activity_reservations = relationship(
        "ActivityReservation", back_populates="booking", cascade="all, delete-orphan"
    )


class HotelReservation(Base):
    __tablename__ = "Hotel_Reservations"
    Reservation_No = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Booking_Id = Column(Integer, ForeignKey("Bookings.Booking_Id"), nullable=False)
    Hotel_Code = Column(Integer, nullable=False)
    Check_In_Date = Column(Date, nullable=False)
    Check_In_Time = Column(String, nullable=True)
    Check_Out_Date = Column(Date, nullable=False)
    Check_Out_Time = Column(String, nullable=True)
    Rate = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="hotel_reservations")


class FlightReservation(Base):
    __tablename__ = "Flight_Reservations"
    Reservation_No = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Booking_Id = Column(Integer, ForeignKey("Bookings.Booking_Id"), nullable=False)
    Airline_Code = Column(String, nullable=False)
    Flight_Number = Column(String, nullable=False)
    Departure_Date = Column(Date, nullable=False)
    Departure_Time = Column(String, nullable=False)
    Arrive_Date = Column(Date, nullable=False)
    Arrive_Time = Column(String, nullable=False)
    Rate = Column(Float, nullable=True)
    Origin_Airport_Code = Column(String, nullable=False)
    Destination_Airport_Code = Column(String, nullable=False)
    Traveling_With_Pets = Column(Boolean, nullable=False, default=False)
    Pet_Count = Column(Integer, nullable=True)

    booking = relationship("Booking", back_populates="flight_reservations")


class ActivityReservation(Base):
    __tablename__ = "Activity_Reservations"
    Activity_Reservation_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Booking_Id = Column(Integer, ForeignKey("Bookings.Booking_Id"), nullable=False)
    Activity_Name = Column(String, nullable=False)
    Location = Column(String, nullable=True)
    Activity_Date = Column(Date, nullable=False)
    Price = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="activity_reservations")

