-- Schema only (no seed data). Used for fresh DB initialization.
DROP TABLE IF EXISTS Activity_Reservations;
DROP TABLE IF EXISTS Flight_Reservations;
DROP TABLE IF EXISTS Hotel_Reservations;
DROP TABLE IF EXISTS Bookings;
DROP TABLE IF EXISTS Airport_Master;
DROP TABLE IF EXISTS Airline_Master;
DROP TABLE IF EXISTS Hotel_Master;
DROP TABLE IF EXISTS Agents;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Phone_Number TEXT,
    Hashed_Password TEXT
);

CREATE TABLE Agents (
    Agent_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Phone TEXT
);

CREATE TABLE Hotel_Master (
    Hotel_Code INTEGER PRIMARY KEY,
    Hotel_Name TEXT NOT NULL,
    Address TEXT,
    City TEXT NOT NULL,
    Zip_Code TEXT,
    Country TEXT NOT NULL,
    Email TEXT,
    Phone_Number TEXT,
    Pet_Friendly INTEGER NOT NULL DEFAULT 0,
    Pet_Fee_Per_Night REAL,
    Max_Pets INTEGER,
    UNIQUE(Hotel_Name, City, Country)
);

CREATE TABLE Airline_Master (
    Airline_Code TEXT PRIMARY KEY,
    Airline_Name TEXT NOT NULL
);

CREATE TABLE Airport_Master (
    Airport_Code TEXT PRIMARY KEY,
    Airport_Name TEXT NOT NULL,
    City TEXT NOT NULL,
    Country TEXT NOT NULL
);

CREATE TABLE Bookings (
    Booking_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_Id INTEGER NOT NULL,
    Agent_Id INTEGER,
    Start_Date TEXT NOT NULL,
    End_Date TEXT NOT NULL
);

CREATE TABLE Hotel_Reservations (
    Reservation_No INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL,
    Hotel_Code INTEGER NOT NULL,
    Check_In_Date TEXT NOT NULL,
    Check_In_Time TEXT,
    Check_Out_Date TEXT NOT NULL,
    Check_Out_Time TEXT,
    Rate REAL,
    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id),
    FOREIGN KEY (Hotel_Code) REFERENCES Hotel_Master(Hotel_Code)
);

CREATE TABLE Flight_Reservations (
    Reservation_No INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL,
    Airline_Code TEXT NOT NULL,
    Flight_Number TEXT NOT NULL,
    Departure_Date TEXT NOT NULL,
    Departure_Time TEXT NOT NULL,
    Arrive_Date TEXT NOT NULL,
    Arrive_Time TEXT NOT NULL,
    Rate REAL,
    Origin_Airport_Code TEXT NOT NULL,
    Destination_Airport_Code TEXT NOT NULL,
    Traveling_With_Pets INTEGER NOT NULL DEFAULT 0,
    Pet_Count INTEGER,
    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id),
    FOREIGN KEY (Airline_Code) REFERENCES Airline_Master(Airline_Code),
    FOREIGN KEY (Origin_Airport_Code) REFERENCES Airport_Master(Airport_Code),
    FOREIGN KEY (Destination_Airport_Code) REFERENCES Airport_Master(Airport_Code)
);

CREATE TABLE Activity_Reservations (
    Activity_Reservation_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL,
    Activity_Name TEXT NOT NULL,
    Location TEXT,
    Activity_Date TEXT NOT NULL,
    Price REAL,
    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id)
);
