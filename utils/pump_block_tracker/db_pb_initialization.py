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

# tabela z identyfikatorem:
"""
CREATE TABLE pb_identifier (
pb_id_val INT);
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
