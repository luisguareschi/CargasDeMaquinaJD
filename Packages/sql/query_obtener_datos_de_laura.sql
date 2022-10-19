DECLARE @temptable TABLE (
    Id INT NOT NULL,
    Code VARCHAR(MAX) NOT NULL,
    Date datetime
);


INSERT INTO @temptable
select Planification.Id, Department.Code, Planification.Date
FROM Planification
INNER JOIN Department
ON Department.Id = Planification.DepartmentId

DECLARE @temptable2 TABLE (
    Id INT NOT NULL,
    Code VARCHAR(MAX) NOT NULL,
    Date datetime
);

INSERT INTO @temptable2
SELECT *     
FROM @temptable T1    
WHERE t1.Id = (
   SELECT max(t2.Id)
   FROM @temptable T2
   WHERE T1.Code=T2.code
)

DECLARE @temptable3 TABLE (
    PlanificationId INT NOT NULL,
	DeliveryDate datetime,
    Reference VARCHAR(MAX) NOT NULL,
	Qty INT
);

INSERT INTO @temptable3
SELECT p.PlanificationId, p.PlanificationDate as DeliveryDate, Reference.Code as Reference, p.Quantity as Qty
FROM PlanificationDetail p
INNER JOIN Reference
ON Reference.Id = p.ReferenceId
--WHERE Reference.Code ='DE20877' and p.PlanificationDate = '20221121 00:00:00' 

select *
from @temptable3 t1
INNER JOIN @temptable2 t2
ON t1.PlanificationId = t2.Id



