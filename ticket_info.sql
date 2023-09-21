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
	stops VARCHAR(40),
	depart_date DATE,
	depart_time clock12h, 
	arrive_time clock12h,
	origin VARCHAR(3),
	destination VARCHAR(3),
	travel_time hour_min, 
	return_date DATE,
	price VARCHAR(15),
	CONSTRAINT pk_expedia PRIMARY KEY(expedia_id)
);
GO

-- Create some custom data to test things out
INSERT INTO expedia (date_scrape) 
VALUES ('2023-9-7 11:00:00'),('2023-9-10 11:00:00'),('2023-9-11 11:00:00'),('2023-9-12 11:00:00');

INSERT INTO expedia (date_scrape) 
VALUES ('2023-9-13 11:00:00');

SELECT * FROM expedia;

DELETE FROM expedia WHERE date_scrape < '2023-9-10';


DELETE FROM expedia 
WHERE GETDATE() > DATEADD(week, 1, date_scrape);



/* This trigger will activate if we make an insert with id > 1000
   Shifts every row and its id back until the oldest entry hits id = 1
   New entries will still be tacked on at the very end as they should
*/
DROP TRIGGER IF EXISTS id_reset;
GO
CREATE TRIGGER id_reset
ON expedia
AFTER INSERT
AS
IF (SELECT MAX(expedia_id) FROM inserted) > 1000
	BEGIN
		SELECT * INTO tmp_expedia FROM expedia;
		DELETE FROM expedia;
		DBCC CHECKIDENT (expedia, RESEED, 0);

		INSERT INTO expedia (date_scrape, airline, stops, depart_time, arrive_time, 
			origin, destination, travel_time, return_date, price) 
		SELECT t.date_scrape, t.airline, t.stops, t.depart_time, t.arrive_time, 
			t.origin, t.destination, t.travel_time, t.return_date, t.price
		FROM tmp_expedia t;

		DROP TABLE tmp_expedia;
	END;
GO



-- We should think about "TRANSACTIONS"


