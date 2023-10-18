USE AirFare;
GO

-- Create rule and data type for 12h PM/AM time
DROP RULE IF EXISTS clocktime12h;
GO
CREATE RULE clocktime12h
AS @value LIKE '%[0-9]:[0-9][0-9] PM'
OR
@value LIKE '%[0-9]:[0-9][0-9] AM';
GO

DROP TYPE IF EXISTS clock12h;
GO
CREATE TYPE clock12h FROM VARCHAR(8);
GO

sp_bindrule clocktime12h, clock12h;

-- Create rule and data type for hours:minutes (00:00) time
DROP RULE IF EXISTS hr_min;
GO
CREATE RULE hr_min
AS @value LIKE '[0-9][0-9]:[0-9][0-9]';
GO

DROP TYPE IF EXISTS hour_min;
GO
CREATE TYPE hour_min FROM VARCHAR(5);
GO

sp_bindrule hr_min, hour_min;

-- Create table for expedia flight tickets
DROP TABLE IF EXISTS expedia;
GO
CREATE TABLE expedia (
	expedia_id INT IDENTITY(1,1),
	date_scrape DATETIME, -- SMALLDATETIME just DOES NOT WORK!
	airline VARCHAR(40),
	ticket_type VARCHAR(15),
	ticket_class VARCHAR(20),
	adults INT,
	children INT,
	infant_lap INT,
	infant_seat INT,
	origin VARCHAR(3),
	destination VARCHAR(3),
	going_stops VARCHAR(40),
	going_date DATE,
	going_time clock12h, 
	going_arrive_time clock12h,
	going_travel_time hour_min, 
	return_date DATE,
	price VARCHAR(15),
	CONSTRAINT pk_expedia PRIMARY KEY(expedia_id)
);
GO

-- Create table for skyscanner flight tickets
DROP TABLE IF EXISTS skyscanner;
GO
CREATE TABLE skyscanner (
	skyscanner_id INT IDENTITY(1,1)
);
GO

-- Create table for kayak flight tickets
DROP TABLE IF EXISTS kayak;
GO
CREATE TABLE kayak (
	kayak_id INT IDENTITY(1,1),
	date_scrape DATETIME,
	airline VARCHAR(40),
	ticket_type VARCHAR(15),
	ticket_class VARCHAR(20),
	adults INT,
	students INT,
	youths INT,
	children INT,
	infant_seat INT,
	infant_lap INT,
	origin VARCHAR(3),
	destination VARCHAR(3),
	going_stops VARCHAR(40),
	going_date DATE,
	going_time clock12h,
	going_arrive_time clock12h,
	going_travel_time hour_min,
	return_stops VARCHAR(40),
	return_date DATE,
	return_time clock12h,
	return_arrive_time clock12h,
	return_travel_time hour_min,
	price VARCHAR(15),
	CONSTRAINT pk_kayak PRIMARY KEY(kayak_id)
);
GO

/* This trigger will activate if we make an insert with id > 1000
   Shifts every row and its id back until the oldest entry hits id = 1
   New entries will still be tacked on at the very end as they should
*/
DROP TRIGGER IF EXISTS id_reset_expedia;
GO
CREATE TRIGGER id_reset_expedia
ON expedia
AFTER INSERT
AS
IF (SELECT MAX(expedia_id) FROM inserted) > 1000
	BEGIN
		SELECT * INTO tmp_expedia FROM expedia;
		DELETE FROM expedia;
		DBCC CHECKIDENT (expedia, RESEED, 0);

		INSERT INTO expedia (date_scrape, airline, ticket_type, ticket_class, 
			adults, children, infant_lap, infant_seat, origin, destination, going_stops, 
			going_time, going_arrive_time, going_travel_time, return_date, price) 
		SELECT t.date_scrape, t.airline, t.ticket_type, t.ticket_class, t.adults, 
			t.children, t.infant_lap, t.infant_seat, t.origin, t.destination, t.going_stops, 
			t.going_time, t.going_arrive_time, t.going_travel_time, t.return_date, t.price
		FROM tmp_expedia t;

		DROP TABLE tmp_expedia;
	END;
GO

DROP TRIGGER IF EXISTS id_reset_kayak;
GO
CREATE TRIGGER id_reset_kayak
ON kayak
AFTER INSERT
AS
IF (SELECT MAX(kayak_id) FROM inserted) > 1000
	BEGIN
		SELECT * INTO tmp_kayak FROM kayak;
		DELETE FROM kayak;
		DBCC CHECKIDENT (kayak, RESEED, 0);

		INSERT INTO kayak (date_scrape, airline, ticket_type, ticket_class, adults, students, 
			youths, children, infant_seat, infant_lap, origin, destination, going_stops, 
			going_date, going_time, going_arrive_time, going_travel_time, return_stops, 
			return_date, return_time, return_arrive_time, return_travel_time, price) 
		SELECT t.date_scrape, t.airline, t.ticket_type, t.ticket_class, t.adults, t.students, 
			t.youths, t.children, t.infant_seat, t.infant_lap, t.origin, t.destination, t.going_stops, 
			t.going_date, t.going_time, t.going_arrive_time, t.going_travel_time, t.return_stops, 
			t.return_date, t.return_time, t.return_arrive_time, t.return_travel_time, t.price
		FROM tmp_kayak t;

		DROP TABLE tmp_kayak;
	END;
GO



-- We should think about "TRANSACTIONS"


SELECT * FROM expedia;
SELECT * FROM kayak;