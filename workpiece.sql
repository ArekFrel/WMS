USE [PRODUKCJAWORKFLOW]
GO

/****** Object:  View [dbo].[Table_Laser]    Script Date: 2023-11-21 15:17:52 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

Create View [dbo].[Table_Laser] As 

	Select 	
		T.PO,
		[Laser_daty].S as Laser_S,
		[Laser_daty].F as Laser_F,		
		Laser.[Laser] As [Laser],
			
		(
		    Num.NumberLaser - Cast(COALESCE(Laser.Laser, 0 ) As Float )
                            ) / Num.NumberLaser As Laser_Progress	
	    From
		(Select  Po, id, Status_Op From Technologia) T
		Left Join (Select * From [dbo].[Laser_daty]()) [Laser_daty]
			on [Laser_daty].PO = T.PO
		Left Join No_of_Laser Laser ON Laser.PO = T.PO
		Left Join No_Of_Laser_all Num ON Num.PO = T.PO

		WHERE 
		T.Status_Op IN (1,2,3,4,5,6)
		Group By
		T.PO,
		[Laser_daty].S ,
		[Laser_daty].F,
		Laser.[Laser],
		Num.NumberLaser
GO


