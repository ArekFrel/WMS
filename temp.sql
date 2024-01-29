		,[Piły_daty].S as Piły_S
		,[Piły_daty].F as Piły_F
		,Pily[Piły] As [Laser]
		,(NumP.NumberPiły - Cast(COALESCE(Piły.Piły, 0 ) As Float )) / NumP.NumberPiły As Laser_Progress



		Left Join (Select * From [dbo].[Piły_daty]()) [Piły_daty] on [Piły_daty].PO = T.PO
		Left Join No_of_Piły Piły ON Piły.PO = T.PO
		Left Join No_Of_Piły_all NumP ON NumP.PO = T.PO

-- Piły

		,[Piły_daty].S
		,[Piły_daty].F
		,Pily[Piły]
