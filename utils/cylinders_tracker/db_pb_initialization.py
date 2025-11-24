# tabela zleceń:

"""
[dbo].[pump_block_orders](
[po] [int] NOT NULL,
[pcs] [int] NULL,
[PB_NAME] [varchar](64) NULL,
[drawing_added] [bit] NULL,
[multiplied_tech] [bit] NULL,
[pcs_started] [int] NULL,
[pcs_finished] [int] NULL,
[pcs_rejected] [int] NULL,
[pcs_stopped] [int] NULL,
"""

# tabele cylindry:
"""
CREATE TABLE cylinders_stock (
    cylinder_type VARCHAR(48) PRIMARY KEY,
    flanges_pcs INT,
    sleeves_pcs INT,
    tubes_pcs INT);

CREATE TABLE cylinders_orders (
	[po] [int] NOT NULL,
	[pcs] [int] NULL,
	[part] [varchar](32) NULL,
	[type] [varchar](64) NULL,
	[name] [varchar](64) NULL,
	[status] [varchar](10) NULL,
	[stocks_counted] [bit] NULL,
	[multiplied] [bit] NULL
);
"""
# wyzwalacz dla pb_identifier:
"""
CREATE TRIGGER block_insert_above_1
ON pb_identifier
INSTEAD OF INSERT
AS
BEGIN
    -- Sprawdzenie liczby rekordów w tabeli
    IF (SELECT COUNT(*) FROM pb_identifier) >= 1
    BEGIN
        -- Jeśli jest już jeden rekord, rzucenie błędu
        RAISERROR ('Only one record is allowed in the table', 16, 1);
    END
    ELSE
    BEGIN
        -- Jeśli nie ma rekordu, wykonanie wstawiania
        INSERT INTO pb_identifier (pb_id_val)
        SELECT pb_id_val FROM inserted;
    END
END;
"""
# stworzenie tabeli PB_NC

"""
CREATE TABLE cylinders_orders (
	[po] [int] NOT NULL,
	[pcs] [int] NOT NULL,
	[part] [varchar](32) NOT NULL,
	[type] [varchar](64) NOT NULL,
	[name] [varchar](64) NOT NULL,
	[status] [varchar](10) NOT NULL,
	[stocks_counted] [bit] NOT NULL,
	[multiplied] [bit] NULL
);
"""